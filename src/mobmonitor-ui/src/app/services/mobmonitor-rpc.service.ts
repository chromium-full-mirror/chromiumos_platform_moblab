import {catchError} from 'rxjs/operators';
import {Injectable, OnDestroy} from '@angular/core';
import {HttpClient, HttpParams, HttpHeaders} from '@angular/common/http';
import {
  Observable,
  Subject,
  Subscription,
  timer,
  Subscriber,
  throwError,
  of
} from 'rxjs';
import {MatDialog} from '@angular/material/dialog';
import {HealthCheck} from '../shared/health-check';
import {Action} from '../shared/action';
import {ActionInfo} from '../shared/action-info';
import {RepairServiceInfo} from '../shared/repair-service-info';
import {ActionsParamDialogComponent} from './actions-param-dialog/actions-param-dialog.component';
import {MobmonitorError, wrapError} from '../shared/mobmonitor-error';
import {Diagnostic} from '../shared/diagnostic';
import {DiagnosticResult} from '../shared/diagnostic-result';
import {RunDiagnosticParams} from '../shared/run-diagnostic-params';

@Injectable()
export class MobmonitorRpcService implements OnDestroy {
  // subject to bind GetStatus updates to
  private getStatusSubject: Subject<Array<HealthCheck>>;

  // indicates that an action is currently running and no status updates
  // should go out. mainly used to prevent UI from repainting and messing up
  // UX
  private repairing: boolean;
  // subscription to the timer observable, we need to clean it up if
  // the service is destroyed
  private timerSub: Subscription;

  constructor(private http: HttpClient, public dialog: MatDialog) {}

  ngOnDestroy() {
    this.timerSub.unsubscribe();
  }

  /**
  Get an observable that intermittently emits new health check updates

  @return observable that emits an array of updated healthchecks every
    1000ms
  */
  getStatus(): Observable<Array<HealthCheck>> {
    if (!this.getStatusSubject) {
      this.initGetStatusTimer();
    }
    return this.getStatusSubject.asObservable();
  }

  // only initialize this timer on demand
  private initGetStatusTimer() {
    // create a singleton that polls for updates to status.
    // all components that need the status will be pushed
    // updates and not need to issue extra HTTP requests
    this.getStatusSubject = new Subject<Array<HealthCheck>>();
    this.timerSub = timer(50, 10000).subscribe(() => {
      if (this.repairing) {
        return;
      }
      this.http.get('/GetStatus').subscribe(
        data => {
          this.getStatusSubject.next(this.handleGetStatus(data));
        },
        error => {
          // emitting an error will kill the subject and make it unable
          // to emit any new events if the connection is re-established
          // so just handle the error on the subscriber side by detecting
          // a time delta
        }
      );
    });
  }

  /**
  formats an http GetStatus response into a HealthCheck object

  @param data raw json data received from http response
  @return array of healthchecks derived from the json response
  */
  private handleGetStatus(data): Array<HealthCheck> {
    const response = [];
    for (const service of data) {
      // partition failed checks into errors and warnings
      // pipe properties into correct fields
      const errors = [];
      const warnings = [];
      for (const check of service.healthchecks) {
        const pushTo = check.health ? warnings : errors;
        pushTo.push({
          name: check.name,
          description: check.description,
          actions: check.actions || {}
        });
      }
      // figure out what status label to use
      let status;
      if (service.health && warnings.length > 0) {
        status = 'warning';
      } else if (service.health) {
        status = 'healthy';
      } else {
        status = 'unhealthy';
      }
      response.push({
        service: service.service,
        health: status,
        errors,
        warnings
      });
    }

    return response;
  }

  /**
  Performs all api calls and gathers any parameters required to run an action

  @param action The action to run
  @return Observable<boolean> indicating whether an action was attempted or not
    If users failed to select parameters, the action will not be run
  */
  runAction(action: Action): Observable<boolean> {
    return new Observable(observer => {
      this.repairing = true;
      this.getActionInfo(action).subscribe(
        actionInfo => {
          // does this action require parameters
          // compare the actionInfo.params to an empty object
          if (JSON.stringify(actionInfo.params) !== JSON.stringify({})) {
            // need to open a params dialog, then run the action
            this.runActionWithParams(action, actionInfo, observer);
          } else {
            this.runActionWithoutParams(action, actionInfo, observer);
          }
        },
        error => {
          this.repairing = false;
          observer.error(wrapError(error, 'Failed to gather action info'));
        }
      );
    });
  }

  /**
  Run an action and request parameters via ActionsParamDialogComponent

  @param action the action to run
  @param actionInfo information including required params for the action
  @param observer subscriber that should be emitted to when action is run
    or determined to not be run
  */
  private runActionWithParams(
    action: Action,
    actionInfo: ActionInfo,
    observer: Subscriber<boolean>
  ) {
    const dialogRef = this.dialog.open(ActionsParamDialogComponent, {
      width: '600px',
      data: actionInfo
    });

    dialogRef.afterClosed().subscribe(
      params => {
        // user entered all required params into the dialog
        if (params) {
          const repairServiceInfo: RepairServiceInfo = {
            service: action.service,
            healthcheck: action.healthCheck,
            action: action.action,
            params: params
          };
          this.repairService(repairServiceInfo).subscribe(() => {
            this.repairing = false;
            observer.next(true);
          });
          // user did not finish the form
        } else {
          this.repairing = false;
          observer.next(false);
        }
      },
      error => {
        this.repairing = false;
        observer.error(wrapError(error, 'Failed to repair service'));
      }
    );
  }

  /**
  Run an action that requires no extra params

  @param action the action to run
  @param actionInfo information including required params for the action
  @param observer subscriber that should be emitted to when action is run
    or determined to not be run
  */
  private runActionWithoutParams(
    action: Action,
    actionInfo: ActionInfo,
    observer: Subscriber<boolean>
  ) {
    const repairServiceInfo: RepairServiceInfo = {
      service: action.service,
      healthcheck: action.healthCheck,
      action: action.action,
      params: {}
    };
    this.repairService(repairServiceInfo).subscribe(
      () => {
        this.repairing = false;
        observer.next(true);
      },
      error => {
        this.repairing = false;
        observer.error(wrapError(error, 'Failed to repair service'));
      }
    );
  }

  /**
  Run http request to get information about a check's action

  @param action the action to gather information on
  @return observable that resolves to the gather action information
  */
  private getActionInfo(action: Action): Observable<ActionInfo> {
    const params = new HttpParams()
      .set('action', action.action)
      .set('healthcheck', action.healthCheck)
      .set('service', action.service);
    return this.http.get<ActionInfo>('/ActionInfo', {params: params});
  }

  /**
  Run http request to perform the described repair action

  @param repairServiceInfo the repair action to perform
  @return observable indicated http request has completed, not necessarily that
    the action was successful.
  */
  private repairService(repairServiceInfo: RepairServiceInfo): Observable<any> {
    const params = new HttpParams()
      .set('action', repairServiceInfo.action)
      .set('healthcheck', repairServiceInfo.healthcheck)
      .set('service', repairServiceInfo.service)
      .set('params', JSON.stringify(repairServiceInfo.params));
    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });
    return this.http.post('/RepairService', params.toString(), {headers});
  }

  /**
   * Run http request to list all available diagnostics
   *
   * @return observable that resolves to a list of supported Diagnostics
   */
  listDiagnostics(): Observable<Diagnostic[]> {
    // TODO - figure out how to catch errors from get calls.
    return this.http.get<Diagnostic[]>('/ListDiagnosticChecks');
  }

  /**
   * Run http request to run a diagnostic
   * @param diagnosticParams params indicating which diagnostic to run
   * @return observable resolving to a DiagnosticResult containing the data gathered from the diagnostic
   */
  runDiagnostic(
    diagnosticParams: RunDiagnosticParams
  ): Observable<DiagnosticResult> {
    const params = new HttpParams()
      .set('category', diagnosticParams.category)
      .set('name', diagnosticParams.name);
    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });
    // TODO - figure out how to catch errors from get calls.
    return this.http.post<DiagnosticResult>(
      '/RunDiagnosticCheck',
      params.toString(),
      {
        headers
      }
    );
  }
}
