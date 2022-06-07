import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class MoblabRebootCheckService {
  private mobmonitorUrl: string;

  constructor(private http: HttpClient) {
    const url = new URL(window.location.href);
    const hostname = environment.defaultHostName || url.hostname;
    const port = environment.defaultApiPort || url.port;
    this.mobmonitorUrl = new String(url.protocol).concat(
      '//',
      hostname,
      ':',
      port,
      '/api/mobmonitor'
    );
  }

  public getStartTime(): Observable<MoblabStartTime[]> {
    return this.http.get<MoblabStartTime[]>(
      this.mobmonitorUrl + '/GetMoblabStartTime'
    );
  }

  public async getMoblabStartTime(): Promise<string> {
    const response: MoblabStartTime[] = await this.getStartTime().toPromise();
    return response['startTime'];
  }

  public async getMoblabUptime(): Promise<string> {
    const response: MoblabStartTime[] = await this.getStartTime().toPromise();
    return response['uptime'];
  }
}

export interface MoblabStartTime {
  startTime: string;
  uptime: string;
}
