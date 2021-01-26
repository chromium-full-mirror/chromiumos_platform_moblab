import {Injectable} from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {MoblabConfigurationGrpcService} from 'app/services/moblab-configuration-grpc.service';

// The service provides live updates to test runner status.
// Subscribe to pauseRequestors observable to recieve live
// updates on job scheduling pause requests.
@Injectable({providedIn: 'root'})
export class MoblabSettingsService {
  private pauseRequestorsSubject = new BehaviorSubject<string[]>([]);
  public pauseRequestors = this.pauseRequestorsSubject.asObservable();

  // Starting a background process to check on system pause state
  constructor(private grpcService: MoblabConfigurationGrpcService) {
    this.grpcService.subscribeToPauseStatusUpdates((pauseRequesters: string[]) =>
      this.updateHostSchedulingStatus(pauseRequesters)
    );
  }

  public updateHostSchedulingStatus(pauseRequesters: string[]): void {
    try {
      this.pauseRequestorsSubject.next(pauseRequesters);
    } catch (ex) {
      console.log('UpdateHostSchedulingStatus error: ' + ex.message);
    }
  }
}
