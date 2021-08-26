import {Component, EventEmitter, Inject, Output} from '@angular/core';
import {MoblabGrpcService} from '../../services/moblab-grpc.service';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogRef,
} from '@angular/material/dialog';

import {ConfirmationDialog} from '../confirmation-dialog/confirmation-dialog.component';
import {NotificationsService} from 'app/services/notifications.service';

@Component({
  selector: 'app-reboot-button',
  templateUrl: './reboot-button.component.html',
})
export class RebootButtonComponent {
  constructor(
    private dialog: MatDialog,
    private moblabGrpcService: MoblabGrpcService,
    private notificationsService: NotificationsService
  ) {}

  rebootClick(): void {
    const dialogRef = this.dialog.open(ConfirmationDialog, {
      width: '500px',
      data: {
        message: 'Are you sure you would like to reboot now?',
        title: 'Reboot',
      },
    });

    const sub = dialogRef.componentInstance.onOk.subscribe(() => {
      this.rebootMoblab();
    });
  }

  rebootMoblab(): void {
    this.moblabGrpcService.reboot_moblab((error_message: string) => {
      this.notificationsService.error(error_message);
    });
  }
}
