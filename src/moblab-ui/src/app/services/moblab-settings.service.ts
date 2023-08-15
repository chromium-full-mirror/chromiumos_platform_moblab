import {Injectable} from '@angular/core';
import {BehaviorSubject, Observable, merge} from 'rxjs';
import {shareReplay} from 'rxjs/operators';
import {MoblabConfigurationGrpcService} from 'app/services/moblab-configuration-grpc.service';

// The service provides live updates to test runner status.
// Subscribe to pauseRequestors observable to recieve live
// updates on job scheduling pause requests.
@Injectable({providedIn: 'root'})
export class MoblabSettingsService {
  private pauseRequestorsSubject = new BehaviorSubject<string[]>([]);
  public pauseRequestorsObservable: Observable<String[]>;

  // Starting a background process to check on system pause state
  constructor(private grpcService: MoblabConfigurationGrpcService) {
    this.pauseRequestorsObservable = merge(
      this.pauseRequestorsSubject.asObservable(),
      this.grpcService.pauseStateObservable
    ).pipe(shareReplay(1));
  }

  public updateHostSchedulingStatus(pauseRequesters: string[]): void {
    try {
      this.pauseRequestorsSubject.next(pauseRequesters);
    } catch (ex) {
      console.log(`UpdateHostSchedulingStatus error: ${ex}`);
    }
  }
}
