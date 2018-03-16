import { Component, OnInit, Input } from '@angular/core';
import { MatSnackBar } from '@angular/material';

import { MobmonitorRpcService } from '../services/mobmonitor-rpc.service';
import { Action } from '../shared/action';
import { ActionInfo } from '../shared/action-info';
import { RepairServiceInfo } from '../shared/repair-service-info';

@Component({
  selector: 'mob-actions',
  templateUrl: './actions.component.html',
  styleUrls: ['./actions.component.scss']
})
export class ActionsComponent implements OnInit {

  @Input()
  private actions: Action[];
  private actionRunning;

  constructor(private rpc: MobmonitorRpcService, public snackBar: MatSnackBar) { }

  ngOnInit() {
    this.actionRunning = {};
    for (const action of this.actions) {
      this.actionRunning[action.action] = false;
    }
  }

  onActionClick(action: Action) {
    this.actionRunning[action.action] = true;
    this.rpc.runAction(action).subscribe(() => {
      this.actionRunning[action.action] = false;
      this.snackBar.open(`Action ${action.action} complete`, 'OK', {
        duration: 2000
      });
    });
  }

}
