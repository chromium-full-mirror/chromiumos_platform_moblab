import {Component, OnInit, ViewChild} from '@angular/core';
import {MatTableDataSource} from '@angular/material/table';

import {ConnectedDutInfo} from 'app/services/moblabrpc_pb';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {ViewDutsComponent} from '../view-duts/view-duts.component';


@Component({
  selector: 'app-enrollment',
  templateUrl: './enrollment.component.html',
  styleUrls: ['./enrollment.component.scss']
})

export class EnrollmentComponent implements OnInit {
  @ViewChild(ViewDutsComponent) dutsTableRef: ViewDutsComponent;
  duts = new MatTableDataSource<ConnectedDutInfo>();

  constructor(private moblabGrpcService: MoblabGrpcService) {}

  ngOnInit() {
  }

  enrollSelected() {
    const hostnames: string[] = this.dutsTableRef.getSelectedDutHostnames();
    this.moblabGrpcService.enrollDuts(hostnames, () => {
      this.dutsTableRef.getConnectedDuts();
    });
  }

  unenrollSelected() {
    const hostnames: string[] = this.dutsTableRef.getSelectedDutHostnames();
    this.moblabGrpcService.unenrollDuts(hostnames, () => {
      this.dutsTableRef.getConnectedDuts();
    });
  }
}
