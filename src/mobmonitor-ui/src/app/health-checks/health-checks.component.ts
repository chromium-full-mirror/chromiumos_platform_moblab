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
      value => this.healthChecks = value
    );
  }

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
