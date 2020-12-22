import {Injectable} from '@angular/core';
import {BehaviorSubject, timer} from 'rxjs';
import {startWith} from 'rxjs/operators';
import {interval} from 'rxjs/internal/observable/interval';
import {MoblabConfigurationGrpcService} from 'app/services/moblab-configuration-grpc.service';

// The service provides live updates to test runner status.
// Subscribe to pauseRequestors observable to recieve live
// updates on job scheduling pause requests.
@Injectable({providedIn: 'root'})
export class MoblabSettingsService {
  private pauseRequestorsSubject = new BehaviorSubject<string[]>([]);
  public pauseRequestors = this.pauseRequestorsSubject.asObservable();

  constructor(private grpcService: MoblabConfigurationGrpcService) {
    interval(5000)
      .pipe(startWith(0))
      .subscribe(i => this.readHostSchedulingStatus());
  }

  updateHostSchedulingStatus(pauseRequesters: string[]): void {
    this.pauseRequestorsSubject.next(pauseRequesters);
  }

  private async readHostSchedulingStatus() {
    try {
      const pause_requesters = await this.grpcService.get_pause_state();
      this.pauseRequestorsSubject.next(pause_requesters);
    } catch (ex) {
      console.log(
        'Get job scheduler pause state background call failed: ' + ex.message
      );
    }
  }
}
