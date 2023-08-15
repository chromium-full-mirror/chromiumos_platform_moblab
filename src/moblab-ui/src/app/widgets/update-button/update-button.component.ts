import {Component, ViewChild} from '@angular/core';
import {MoblabGrpcService} from '../../services/moblab-grpc.service';
import {MatDialog} from '@angular/material/dialog';
import {OnInit} from '@angular/core';
import {ButtonWithProgressComponent} from '../button-with-progress/button-with-progress.component';

import {ConfirmationDialog} from '../confirmation-dialog/confirmation-dialog.component';
import {NotificationsService} from 'app/services/notifications.service';

@Component({
  selector: 'app-update-button',
  templateUrl: './update-button.component.html',
  styleUrls: ['./update-button.component.scss'],
})
export class UpdateButtonComponent implements OnInit {
  @ViewChild('updateBUtton') updateButton: ButtonWithProgressComponent;
  isUpdateAvailable = false;
  getUpdateStatusFailed = false;
  statusMessage = 'No updates found';

  constructor(
    private moblabGrpcService: MoblabGrpcService,
    private dialog: MatDialog,
    private notificationsService: NotificationsService
  ) {}

  ngOnInit(): void {
    this.moblabGrpcService.get_is_update_available(
      (is_update_available: boolean) => {
        this.isUpdateAvailable = is_update_available;
      },
      (msg: string) => {
        this.getUpdateStatusFailed = true;
        this.statusMessage = this.getUpdateStatusMessage();
        this.notificationsService.error(msg);
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
    this.updateButton.setIsLoadingStatus(true);
    this.moblabGrpcService.update_moblab(
      (message: string) => {
        this.updateButton.setIsLoadingStatus(false);
        this.notificationsService.notify(message);
      },
      (error_message: string) => {
        this.updateButton.setIsLoadingStatus(false);
        this.notificationsService.error(error_message);
      }
    );
  }
}
