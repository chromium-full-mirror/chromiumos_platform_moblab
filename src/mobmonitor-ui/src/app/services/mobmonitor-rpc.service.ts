import { Injectable, OnDestroy } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { Subject } from 'rxjs/Subject';
import { Subscription } from 'rxjs/Subscription';
import { multicast } from 'rxjs/operators';
import { interval } from 'rxjs/observable/interval';

import { HealthCheck } from '../shared/health-check';
import { Action } from '../shared/action';
import { ActionInfo } from '../shared/action-info';
import { RepairServiceInfo } from '../shared/repair-service-info';

@Injectable()
export class MobmonitorRpcService implements OnDestroy {

  private getStatusSubject: Subject<Array<HealthCheck>>;
  private repairing: boolean;
  private intervalSub: Subscription;

  constructor(private http: HttpClient) {
    // create a singleton that polls for updates to status
    // all components that need the status will be pushed
    // updates and not need to issue extra HTTP requests
    this.getStatusSubject = new Subject<Array<HealthCheck>>();
    this.intervalSub = interval(1000).subscribe(() => {
      if (this.repairing) { return; }
      this.http.get('/GetStatus').subscribe(data => {
        this.getStatusSubject.next(this.handleGetStatus(data));
      });
    });
  }

  ngOnDestroy() {
    this.intervalSub.unsubscribe();
  }

  getStatus(): Observable<Array<HealthCheck>> {
    return this.getStatusSubject.asObservable();
  }

  // formats an RPC GetStatus response into a HealthCheck object
  private handleGetStatus(data): Array<HealthCheck> {
    const response = [];
    for (const service of data) {
      // partition failed checks into errors and warnings
      // pipe properties into correct fields
      const errors = [];
      const warnings = [];
      for (const check of service.healthchecks) {
        const pushTo = (check.health) ? warnings : errors;
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

  runAction(action: Action): Observable<any> {
    return new Observable(observer => {
      this.repairing = true;
      this.getActionInfo(action).subscribe(actionInfo => {
        const repairServiceInfo: RepairServiceInfo = {
          service: action.service,
          healthcheck: action.healthCheck,
          action: action.action,
          args: [],
          kwargs: {}
          // TODO (mattmallett@ crbug.com/824884)
        };
        this.repairService(repairServiceInfo).subscribe(() => {
          this.repairing = false;
          observer.next();
        });
      });
    });

  }

  private getActionInfo(action: Action): Observable<ActionInfo> {
    const params = new HttpParams()
      .set('action', action.action)
      .set('healthcheck', action.healthCheck)
      .set('service', action.service);
    return this.http.get<ActionInfo>('/ActionInfo', {params: params});
  }

  private repairService(repairServiceInfo: RepairServiceInfo): Observable<any> {
    const params = new HttpParams()
      .set('action', repairServiceInfo.action)
      .set('healthcheck', repairServiceInfo.healthcheck)
      .set('service', repairServiceInfo.service)
      .set('args', JSON.stringify(repairServiceInfo.args))
      .set('kwargs', JSON.stringify(repairServiceInfo.kwargs));
    const headers = new HttpHeaders({'Content-Type': 'application/x-www-form-urlencoded'});
    return this.http.post('/RepairService', params.toString(), {headers});
  }

}
