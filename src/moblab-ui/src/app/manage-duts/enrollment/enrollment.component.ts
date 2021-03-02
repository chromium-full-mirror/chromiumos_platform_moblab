import {Component, ViewChild} from '@angular/core';
import {MatSnackBar} from '@angular/material/snack-bar';
import {MatTableDataSource} from '@angular/material/table';
import {MatDialog} from '@angular/material/dialog';
import {Router} from '@angular/router';


import {ConnectedDutInfo} from 'app/services/moblabrpc_pb';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {ViewDutsComponent} from '../view-duts/view-duts.component';
import {ProvisionDialogComponent} from '../provision-dialog/provision-dialog.component'

@Component({
  selector: 'app-enrollment',
  templateUrl: './enrollment.component.html',
  styleUrls: ['./enrollment.component.scss'],
})
export class EnrollmentComponent {
  @ViewChild(ViewDutsComponent) dutsTableRef: ViewDutsComponent;
  duts = new MatTableDataSource<ConnectedDutInfo>();

  constructor(
    private moblabGrpcService: MoblabGrpcService,
    private snackBar: MatSnackBar,
    private router: Router,
    public dialog: MatDialog
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
        this.reportError(msg);
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
        this.reportError(msg);
        this.dutsTableRef.stopLoadingSpinner();
      }
    );
  }

  reportError(dialogue: string) {
    this.snackBar.open(dialogue, '', {
      duration: 5000,
      verticalPosition: 'top',
    });
  }

  provisionDuts() {
    if (!this.dutsTableRef.duts.data) {
      this.reportError("You need to have at least one enrolled DUT")
      return;
    }

    const dialogRef = this.dialog.open(ProvisionDialogComponent,
      {data: {duts: this.dutsTableRef.duts.data}});

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        let duts = this.dutsTableRef.duts.data;
        if (result.pool) {
          duts = duts.filter((value) => {return result.pool in value.getPoolsList();})
        }
        this.moblabGrpcService.provisionDuts(
          () => {
            this.dutsTableRef.stopLoadingSpinner();
            this.router.navigate(['/view_jobs']);
          },
          (errorMessage: string) => {
            this.dutsTableRef.stopLoadingSpinner();
            this.reportError(errorMessage);
          },
          result.buildVersion,
          result.milestone,
          result.pool);
        this.dutsTableRef.startLoadingSpinner();
      }
    });
  }
}
