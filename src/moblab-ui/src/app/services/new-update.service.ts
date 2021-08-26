import {Injectable} from '@angular/core';
import {Observable, BehaviorSubject} from 'rxjs';

import {MoblabGrpcService} from './moblab-grpc.service';
import {Job} from './moblabrpc_pb';
import {NewUpdateStatus} from '../constants';

@Injectable({
  providedIn: 'root',
})
export class NewUpdateService {
  private data$ = new BehaviorSubject({
    status: NewUpdateStatus.UNKNOWN,
    reason: 'Service not called.',
  });
  public newUpdateStatusObservable: Observable<{}> = this.data$.asObservable();

  constructor(private moblabGrpcService: MoblabGrpcService) {}

  pollForUpdates(delay?: number) {
    /**
     * Methods polls for the update status of the Moblab. Must be called at
     * app start up only.
     */
    if (delay === undefined) {
      delay = 300000; // Default delay of 5 minutes.
    }
    this.isUpdateAvailable();
    setTimeout(() => {
      this.pollForUpdates(delay);
    }, delay);
  }

  isUpdateAvailable() {
    /**
     * Method that successively calls required Promises to get the update
     * status of the Moblab in the public Observable.
     */
    this.isUpdateAvailablePromise()
      .then((is_update_available: boolean) => {
        if (is_update_available) {
          this.getNumJobsPromise().then((numJobs: number) => {
            if (numJobs > 0) {
              this.data$.next({
                status: NewUpdateStatus.UPDATE_AVAILABLE_WITH_JOBS_RUNNING,
                reason: '',
              });
            } else {
              this.data$.next({
                status: NewUpdateStatus.UPDATE_AVAILABLE,
                reason: '',
              });
            }
          });
        } else {
          this.data$.next({
            status: NewUpdateStatus.NO_UPDATE,
            reason: '',
          });
        }
      })
      .catch((errorMsg: string) => {
        this.data$.next({
          status: NewUpdateStatus.UNKNOWN,
          reason: errorMsg,
        });
      });
  }

  isUpdateAvailablePromise(): Promise<boolean> {
    /**
     * Convert the get_is_update_available function into a Promise.
     */
    return new Promise((resolve, reject) => {
      this.moblabGrpcService.get_is_update_available(
        (is_update_available: boolean) => {
          resolve(is_update_available);
        },
        (errorMsg: string) => {
          console.log(
            'Failed to get uvailable update information: ' + errorMsg
          );
          reject(false);
        }
      );
    });
  }

  getNumJobsPromise(): Promise<number> {
    /**
     * Convert the getNumJobs function into a Promise.
     */
    return new Promise((resolve, _) => {
      this.moblabGrpcService.getNumJobs(
        (numJobs: number) => {
          resolve(numJobs);
        },
        undefined, // id_filter
        undefined, // name_filter
        undefined, // created_time_lt
        undefined, // created_time_gt
        Job.QueueStatus.JOBS_RUNNING // status_filter
      );
    });
  }
}
