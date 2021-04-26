import {Injectable} from '@angular/core';
import {
  CanActivate,
  Router,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
} from '@angular/router';
import {MoblabHealthCheckService} from '../services/moblab-health-check.service';

@Injectable({
  providedIn: 'root',
})
export class MoblabHealthCheckGuard implements CanActivate {
  constructor(
    private router: Router,
    private healthCheckService: MoblabHealthCheckService
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Promise<boolean> {
    return new Promise(resolve => {
      this.healthCheckService
        .isMoblabServiceHealthy()
        .then(healthy => {
          if (!healthy) {
            this.router.navigate(['/health_check']);
            resolve(false);
          } else {
            resolve(true);
          }
        })
        .catch(error => {
          console.error('Failed to get the status from mobmonitor', error);
          this.router.navigate(['/health_check']);
          resolve(false);
        });
    });
  }
}
