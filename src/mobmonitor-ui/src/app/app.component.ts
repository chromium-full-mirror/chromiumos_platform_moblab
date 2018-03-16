import { Component, OnInit } from '@angular/core';

import { MobmonitorRpcService } from './services/mobmonitor-rpc.service';

@Component({
  selector: 'mob-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  private updated: Date;

  constructor(private rpc: MobmonitorRpcService) {}

  ngOnInit() {
    this.updated = undefined;
    this.rpc.getStatus().subscribe(
      value => this.updated = new Date()
    );
  }

}
