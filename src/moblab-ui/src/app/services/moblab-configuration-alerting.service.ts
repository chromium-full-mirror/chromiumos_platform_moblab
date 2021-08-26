import {Injectable} from '@angular/core';
import {Observable, of, Subject, BehaviorSubject, combineLatest} from 'rxjs';
import {map} from 'rxjs/operators';

@Injectable()
export class ConfigSetupService {
  private isCloudConfigEnabled = false;
  private error = false;
  private enabled$ = new BehaviorSubject(this.isCloudConfigEnabled);
  private error$ = new BehaviorSubject(this.error);
  public cloudConfigObservable: Observable<{}> = this.getCloudConfigObservable();

  constructor() {}

  private getCloudConfigObservable(): Observable<{}> {
    return combineLatest([
      this.enabled$.asObservable(),
      this.error$.asObservable(),
    ]).pipe(
      map(data => ({
        enabled: data[0],
        error: data[1],
      }))
    );
  }

  setState(enabled: boolean, error: boolean): void {
    /**
     * Set the state of the service.
     */
    this.setIsCloudConfigEnabled(enabled);
    this.setError(error);
  }

  getError(): boolean {
    /**
     * Get 'error' status of cloud configuration.
     */
    return this.error;
  }

  setError(error: boolean): void {
    /**
     * Set to true when unable to retrieve the status of cloud configuration.
     */
    this.error = error;
    this.error$.next(this.error);
  }

  setIsCloudConfigEnabled(isCloudConfigEnabled: boolean): void {
    /**
     * Set 'enabled' status of cloud configuration.
     */
    this.isCloudConfigEnabled = isCloudConfigEnabled;
    this.enabled$.next(this.isCloudConfigEnabled);
  }

  getIsCloudConfigEnabled(): boolean {
    /**
     * Get if cloud configuration has been enabled.
     */
    return this.isCloudConfigEnabled;
  }
}
