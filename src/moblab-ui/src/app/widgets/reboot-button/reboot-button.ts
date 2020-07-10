import {Component, EventEmitter, Inject, Output} from '@angular/core';
import {MoblabGrpcService} from '../../services/moblab-grpc.service';
import {MatSnackBar} from '@angular/material/snack-bar';
import {MAT_DIALOG_DATA, MatDialog, MatDialogRef} from '@angular/material/dialog';

@Component({
  selector: 'confirmation-dialog',
  templateUrl: './confirmation_dialog.html',
})
export class ConfirmationDialog {
  title = '';
  message = '';

  constructor(
    public dialogRef: MatDialogRef<ConfirmationDialog>,
    private snackBar: MatSnackBar,
    private moblabGrpcService: MoblabGrpcService,
    @Inject(MAT_DIALOG_DATA) public data: any) {
    this.message = data.message;
    this.title = data.title;
  }
  onClick(): void {
    this.moblabGrpcService.reboot_moblab((error_message: string) => {
      this.reportError(error_message);
    });
  }

  reportError(dialogue) {
    const snackBarRef = this.snackBar.open(dialogue, '', {
      duration: 5000,
      verticalPosition: 'top'
    });
  }
}

@Component({
  selector: 'app-reboot-button',
  templateUrl: './reboot-button.component.html',
})
export class RebootButtonComponent{
  constructor(
    private dialog: MatDialog,
  ) {}

  rebootClick(): void {
    const dialogRef = this.dialog.open(ConfirmationDialog, {
      width: '500px',
      data: {
        'message': 'Are you sure you would like to reboot now?',
        'title': 'Reboot'
      }
    });
  }
}
