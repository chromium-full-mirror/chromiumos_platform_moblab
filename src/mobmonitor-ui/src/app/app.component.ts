import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs/Subscription';
import { interval } from 'rxjs/observable/interval';

import { MobmonitorRpcService } from './services/mobmonitor-rpc.service';
import { HealthCheck } from './shared/health-check';

@Component({
  selector: 'mob-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, OnDestroy {

  // time of last successful update
  private updated: Date;

  // indicating that UI has lost connection to the backend
  // essentially in an error state until regular updates begin
  // streaming in
  private lostConnection = false;

  private intervalSub: Subscription;

  constructor(private rpc: MobmonitorRpcService) {}

  ngOnInit() {
    this.updated = undefined;

    this.rpc.getStatus().subscribe(val => {
      this.updated = new Date();
      this.lostConnection = false;
    });

    // every 10 seconds check if we have some recent data
    this.intervalSub = interval(10000).subscribe(() => {
      // check if our latest data is older than 10 seconds
      const tenSecondsAgo = Date.now() - 10000;
      if (this.updated === undefined) {
        this.lostConnection = true;
      } else if (this.updated.getTime() < tenSecondsAgo) {
        this.lostConnection = true;
      }
    });
  }

  ngOnDestroy() {
    this.intervalSub.unsubscribe();
  }

}
