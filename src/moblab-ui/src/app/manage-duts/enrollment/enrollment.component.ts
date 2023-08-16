import { Component, ViewChild } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';

import { ConnectedDutInfo } from 'app/services/moblabrpc_pb';
import { MoblabGrpcService } from 'app/services/moblab-grpc.service';
import { ViewDutsComponent } from '../view-duts/view-duts.component';
import { ProvisionDialogComponent } from '../provision-dialog/provision-dialog.component';
import { NotificationsService } from 'app/services/notifications.service';
@Component({
  selector: 'app-enrollment',
  templateUrl: './enrollment.component.html',
  styleUrls: ['./enrollment.component.scss'],
})
export class EnrollmentComponent {
  @ViewChild(ViewDutsComponent) dutsTableRef: ViewDutsComponent;
  duts = new MatTableDataSource<ConnectedDutInfo>();
  isDUTSelected = false;

  constructor(
    private moblabGrpcService: MoblabGrpcService,
    private router: Router,
    public dialog: MatDialog,
    private notificationsService: NotificationsService
  ) { }

  enrollSelected() {
    this.dutsTableRef.startLoadingSpinner();
    const hostnames: string[] = this.dutsTableRef.getSelectedDutHostnames();
    this.moblabGrpcService.enrollDuts(
      hostnames,
      () => {
        this.dutsTableRef.getConnectedDuts();
      },
      (msg: string) => {
        this.notificationsService.error(msg);
        this.dutsTableRef.stopLoadingSpinner();
      }
    );
  }

  unenrollSelected() {
    this.dutsTableRef.startLoadingSpinner();
    const hostnames: string[] = this.dutsTableRef.getSelectedDutHostnames();
    this.moblabGrpcService.unenrollDuts(
      hostnames,
      () => {
        this.dutsTableRef.getConnectedDuts();
      },
      (msg: string) => {
        this.notificationsService.error(msg);
        this.dutsTableRef.stopLoadingSpinner();
      }
    );
  }

  reverifySelected() {
    this.dutsTableRef.startLoadingSpinner();
    const hostnames: string[] = this.dutsTableRef.getSelectedDutHostnames();
    this.moblabGrpcService.reverifyDuts(
      () => {
        this.dutsTableRef.getConnectedDuts();
      },
      (msg: string) => {
        this.notificationsService.error(msg);
        this.dutsTableRef.stopLoadingSpinner();
      },
      hostnames
    );
  }

  selectedDUTsChanged() {
    this.isDUTSelected = this.dutsTableRef?.selection.selected.length > 0;
  }

  provisionDuts() {
    if (!this.dutsTableRef.duts.data) {
      this.notificationsService.notify(
        'You need to have at least one enrolled DUT'
      );
      return;
    }

    const dialogRef = this.dialog.open(ProvisionDialogComponent, {
      data: { duts: this.dutsTableRef.duts.data },
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        let duts = this.dutsTableRef.duts.data;
        if (result.pool) {
          duts = duts.filter(dut => dut.getPoolsList()?.includes(result.pool));
        }
        this.moblabGrpcService.provisionDuts(
          () => {
            this.dutsTableRef.stopLoadingSpinner();
            this.router.navigate(['/view_jobs']);
          },
          (errorMessage: string) => {
            this.dutsTableRef.stopLoadingSpinner();
            this.notificationsService.error(errorMessage);
          },
          result.buildVersion,
          result.milestone,
          result.pool
        );
        this.dutsTableRef.startLoadingSpinner();
      }
    });
  }
}
