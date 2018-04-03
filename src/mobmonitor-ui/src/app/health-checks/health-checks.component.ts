import { Component, OnInit } from '@angular/core';

import { MobmonitorRpcService } from '../services/mobmonitor-rpc.service';
import { HealthCheck } from '../shared/health-check';
import { Action } from '../shared/action';

@Component({
  selector: 'mob-health-checks',
  templateUrl: './health-checks.component.html',
  styleUrls: ['./health-checks.component.scss']
})
export class HealthChecksComponent implements OnInit {

  private healthChecks: HealthCheck[];

  constructor(private rpc: MobmonitorRpcService) { }

  ngOnInit() {
    this.rpc.getStatus().subscribe(
      value => this.healthChecks = value,
      error => {} // can't really do anything with the error
      // the app component will notify user of lost connection
    );
  }

  /**
  Get the label that will be printed for a given healthcheck status

  @param healthCheck the healthcheck to get a label for
  @return a label for the current status of the healthcheck
  */
  getHealthCheckLabel(healthCheck: HealthCheck): string {
    switch (healthCheck.health) {
      case 'unhealthy':
        return 'not healthy';
      case 'warning':
        return 'healthy with warnings';
      case 'healthy':
      default:
        return healthCheck.health;
    }
  }

  /**
  Construct an array of action objects from the healthcheck

  @param healthCheck the healthcheck to extract actions from
  @param checkName the specific check to extract actions for, this is the
    Action.healthCheck value
  @return an array of Actions that are available for the specified check
  */
  getActionsForCheck(healthCheck: HealthCheck, checkName: string): Action[] {
    const check = healthCheck.errors.filter(c => c.name === checkName)[0];

    if (check) {
      const actions = [];
      for (const action of check.actions) {
        actions.push({
          action,
          service: healthCheck.service,
          healthCheck: check.name
        });
      }
      return actions;
    }
    return [];
  }

}
