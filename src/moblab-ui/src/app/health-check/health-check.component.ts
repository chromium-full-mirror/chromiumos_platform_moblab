import {Component, OnInit, OnDestroy} from '@angular/core';
import {Subscription, timer} from 'rxjs';
import {Router} from '@angular/router';
import {GlobalInfoService} from '../services/global-ui-settings.service';
import {
  MoblabHealthCheckService,
  HealthCheck,
  ServiceHealthCheck,
} from '../services/moblab-health-check.service';
import {MoblabHealthCheckConstants} from '../constants';

@Component({
  selector: 'app-health-check',
  templateUrl: './health-check.component.html',
  styleUrls: [
    './health-check.component.scss',
    '../configuration/configuration.component.scss',
  ],
})
export class HealthCheckComponent implements OnInit, OnDestroy {
  serviceHealthChecks: ServiceHealthCheck[] = [];
  isMobMonitorHealthy: boolean;
  loadingPercentage: number;
  moblabServiceHealth: ServiceHealthCheck;
  failedHealthChecks: HealthCheck[] = [];
  loadingContainers: HealthCheck[] = [];
  expectedContainers = MoblabHealthCheckConstants.MOBLAB_CONTAINERS_COUNT;
  mobmonitorLink = this.getMobmonitorLink();
  subscription: Subscription;

  /** This list is used to remove failed health checks that have dependencies */
  private failedCheckDependencies = [
    {
      name: 'ServiceAccountFile',
      dependency: 'BotoFile',
    },
  ];

  /** List of errors to bypass so the redirect can go through */
  private failedCheckIgnoreList = ['BotoFile'];

  constructor(
    private router: Router,
    private healthCheckService: MoblabHealthCheckService,
    private globalInfoService: GlobalInfoService
  ) { }

  ngOnInit(): void {
    this.globalInfoService.setEnableNavBar(false);
    this.subscription = timer(1000, 20000).subscribe(() => {
      this.healthCheckService.getMobmonitorHealthCheck().subscribe({
        next: data => {
          this.handleMoblabHealthCheck(data);
        },
        error: error => {
          this.isMobMonitorHealthy = false;
          console.error(
            'Failed to get the health status from mobmonitor',
            error
          );
        },
      });
    });
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
    this.globalInfoService.setEnableNavBar(true);
  }

  handleMoblabHealthCheck(services: ServiceHealthCheck[]) {
    this.isMobMonitorHealthy = true;
    this.serviceHealthChecks = services;

    this.moblabServiceHealth = services.filter(
      data => data.service === 'moblab'
    )[0];

    this.loadingContainers = this.moblabServiceHealth.healthchecks.filter(
      container => container.health === true
    );

    const failedHealthChecks = this.moblabServiceHealth.healthchecks.filter(
      container => container.health === false
    );

    // filter the failed health checks with dependencies
    const failedHealthCheckNames = failedHealthChecks.map(
      failedCheck => failedCheck.name
    );
    const failedChecksToFilter = this.failedCheckDependencies
      .filter(
        failedCheck =>
          failedHealthCheckNames.includes(failedCheck.name) &&
          failedHealthCheckNames.includes(failedCheck.dependency)
      )
      .map(failedCheck => failedCheck.name);
    this.failedHealthChecks = failedHealthChecks.filter(
      failedCheck => !failedChecksToFilter.includes(failedCheck.name)
    );

    this.loadingPercentage =
      ((this.expectedContainers - this.loadingContainers.length) /
        this.expectedContainers) *
      100;

    const criticalFailedChecks = this.failedHealthChecks.filter(
      failedCheck => !this.failedCheckIgnoreList.includes(failedCheck.name)
    );

    const isMoblabHealhty =
      this.loadingContainers.length === 0 && criticalFailedChecks.length === 0;
    if (isMoblabHealhty) {
      this.router.navigate(['/']);
    }
  }

  getMobmonitorLink(): string {
    const hostname = window.location.hostname;
    return `http://${hostname}:9991/static/index.html`;
  }
}
