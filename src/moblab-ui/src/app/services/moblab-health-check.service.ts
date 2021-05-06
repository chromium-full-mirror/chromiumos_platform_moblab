import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {MoblabHealthCheckConstants} from '../constants';

@Injectable({
  providedIn: 'root',
})
export class MoblabHealthCheckService {
  private mobmonitorUrl: string;

  constructor(private http: HttpClient) {
    const url = new URL(window.location.href);
    this.mobmonitorUrl = new String(url.protocol).concat(
      '//',
      url.hostname,
      ':',
      url.port,
      '/api/mobmonitor'
    );
  }

  /**
   * Gets moblab health checks from mobmonitor.
   */
  public getMobmonitorHealthCheck(): Observable<ServiceHealthCheck[]> {
    return this.http.get<ServiceHealthCheck[]>(
      this.mobmonitorUrl + '/GetStatus'
    );
  }

  /**
   * Gets moblab health status from mobmonitor.
   * @return {Promise<boolean>} the boolean health status as a promise.
   */
  public async isMoblabServiceHealthy(): Promise<boolean> {
    const data: ServiceHealthCheck[] = await this.getMobmonitorHealthCheck().toPromise();
    if (data === undefined) {
      return false;
    }
    const moblabService = data.filter(
      service => service.service === 'moblab'
    )[0];

    const loadingContainers = moblabService.healthchecks.filter(
      container => container.health === true
    );
    return loadingContainers.length === 0;
  }
}

export interface ServiceHealthCheck {
  service: string;
  health: boolean;
  healthchecks: Array<HealthCheck>;
}

export interface HealthCheck {
  name: string;
  health: boolean;
  description: string;
  action: string;
}
