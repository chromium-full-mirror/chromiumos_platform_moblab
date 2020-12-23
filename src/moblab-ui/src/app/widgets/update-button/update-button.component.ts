import {Component} from '@angular/core';
import {MoblabGrpcService} from '../../services/moblab-grpc.service';
import {MatSnackBar} from '@angular/material/snack-bar';
import {MatDialog} from '@angular/material/dialog';
import {OnInit} from '@angular/core';

import {ConfirmationDialog} from '../confirmation-dialog/confirmation-dialog.component';

@Component({
  selector: 'app-update-button',
  templateUrl: './update-button.component.html',
  styleUrls: ['./update-button.component.css'],
})
export class UpdateButtonComponent implements OnInit {
  isUpdateAvailable = false;
  getUpdateStatusFailed = false;

  constructor(
    private moblabGrpcService: MoblabGrpcService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.moblabGrpcService.get_is_update_available(
      (is_update_available: boolean) => {
        this.isUpdateAvailable = is_update_available;
      },
      (msg: string) => {
        this.getUpdateStatusFailed = true;
        this.reportError(msg);
      }
    );
  }

  getUpdateStatusMessage() {
    if (this.getUpdateStatusFailed) {
      return 'Failed to get update status.';
    } else if (this.isUpdateAvailable) {
      return 'An update is available!';
    } else {
      return 'No updates found.';
    }
  }

  updateClick(): void {
    const dialogRef = this.dialog.open(ConfirmationDialog, {
      width: '500px',
      data: {
        message:
          'This software update will take 1-2 mins. Please ensure ' +
          'no tests are running before the update. Would you like to proceed?',
        title: 'Update Confirmation',
      },
    });

    dialogRef.componentInstance.onOk.subscribe(() => {
      this.updateMoblab();
    });
  }

  updateMoblab() {
    this.moblabGrpcService.update_moblab(
      (message: string) => {
        this.reportError(message);
      },
      (error_message: string) => {
        this.reportError(error_message);
      }
    );
  }

  reportError(dialogue: string) {
    this.snackBar.open(dialogue, '', {
      duration: 5000,
      verticalPosition: 'top',
    });
  }
}
