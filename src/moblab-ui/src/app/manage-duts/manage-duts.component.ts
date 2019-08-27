import { Component, OnInit } from '@angular/core';
import { ConnectedDutInfo } from 'app/services/moblabrpc_pb';
import { MoblabGrpcService } from 'app/services/moblab-grpc.service';

@Component({
  selector: 'app-manage-duts',
  templateUrl: './manage-duts.component.html',
  styleUrls: ['./manage-duts.component.css']
})
export class ManageDutsComponent implements OnInit {

  constructor(private moblabGrpcService: MoblabGrpcService) {}

  duts = [];
  displayedColumns: string[] = [ 'select', 'name', 'board', 'model', 'status', 'is-enrolled', 'unique-labels'];

  ngOnInit() {
    this.moblabGrpcService.listConnectedDuts((connectedDuts: ConnectedDutInfo[]) => { this.duts = connectedDuts; console.log(connectedDuts); });
  }

  masterToggle() {

  }

}
