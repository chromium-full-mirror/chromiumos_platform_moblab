import {Injectable} from '@angular/core';
import {CanActivate, Router} from '@angular/router';
import {environment} from 'environments/environment';
import {MoblabHealthCheckService} from '../services/moblab-health-check.service';

@Injectable({
  providedIn: 'root',
})
export class MoblabHealthCheckGuard implements CanActivate {
  constructor(
    private router: Router,
    private healthCheckService: MoblabHealthCheckService
  ) {}

  canActivate(): Promise<boolean> | boolean {
    if (environment.disableHealthCheckGuard) {
      return true;
    }

    return this.healthCheckService
      .isMoblabServiceHealthy()
      .then(healthy => {
        if (!healthy) {
          this.router.navigate(['/health_check']);
          return false;
        }
        return true;
      })
      .catch(error => {
        console.error('Failed to get the status from mobmonitor', error);
        this.router.navigate(['/health_check']);
        return false;
      });
  }
}
