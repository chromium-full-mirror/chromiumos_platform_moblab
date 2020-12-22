import {Component, Inject, OnInit, Output, ViewChild} from '@angular/core';
import {
  MatDialog,
  MatDialogRef,
  MAT_DIALOG_DATA,
} from '@angular/material/dialog';

import {MoblabGrpcService} from '../../services/moblab-grpc.service';

const DEFAULT_ERROR_SUFFIX =
  ' If this problem persists, please contact ' + 'chromeos-moblab@google.com';

@Component({
  selector: 'submission-result-dialog',
  template: `
    <h1 mat-dialog-title>{{ title }}</h1>
    <div mat-dialog-content>
      <p>{{ message }}</p>
    </div>
    <div mat-dialog-actions>
      <button mat-button cdkFocusInitial [mat-dialog-close]>Ok</button>
    </div>
  `,
})
export class SubmissionResultDialog {
  title = '';
  message = '';

  constructor(
    public dialogRef: MatDialogRef<SubmissionResultDialog>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.message = data.message;
    this.title = data.title;
  }

  onNoClick(): void {
    this.dialogRef.close();
  }
}

@Component({
  selector: 'app-feedback',
  template: `
    <mat-icon class="feedback-icon" feedback (send)="onSend($event)"
      >feedback</mat-icon
    >
  `,
  styleUrls: [],
})
/**
 * Component for pop-up UI for typing up feedback and submitting screenshots.
 */
export class FeedbackComponent {
  constructor(
    private dialog: MatDialog,
    private moblabGrpcService: MoblabGrpcService
  ) {}

  openDialog(message, title): void {
    const dialogRef = this.dialog.open(SubmissionResultDialog, {
      width: '500px',
      data: {message: message, title: title},
    });
  }
  onSend(event) {
    this.moblabGrpcService.sendMoblabScreenshot(
      (message: string) => {
        this.openDialog(message, 'Feedback Submitted');
      },
      (message: string) => {
        this.openDialog(
          message + DEFAULT_ERROR_SUFFIX,
          'Feedback Submission Failed'
        );
      },
      event.contactEmail,
      event.description,
      event.screenshot
    );
  }
}
