import {Injectable} from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {startWith} from 'rxjs/operators';
import {interval} from "rxjs/internal/observable/interval";
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';

export const USER_REQUEST_STRING = "User request";

// The service provides live updates to test runner status.
// Subscribe to pauseRequestors observable to recieve live 
// updates on job scheduling pause requests.
@Injectable({providedIn: 'root'})
export class MoblabSettingsService {
  private pauseRequestorsSubject = new BehaviorSubject<string[]>([]);
  public pauseRequestors = this.pauseRequestorsSubject.asObservable();

  constructor(private moblabGrpcService: MoblabGrpcService) {
    interval(5000).pipe(startWith(0)).subscribe(i => this.readHostSchedulingStatus());
  }

  updateHostSchedulingStatus(pauseRequesters: string[]): void {
    this.pauseRequestorsSubject.next(pauseRequesters)
  }

  private readHostSchedulingStatus() {
    this.moblabGrpcService.get_pause_state(
      (pause_requesters: string[]) => {
        this.pauseRequestorsSubject.next(pause_requesters);
      },
      (msg: string) => {
        console.log('Get job scheduler pause state background call failed: ' + msg);
      });
  }
}
