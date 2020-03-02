import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

import { MobmonitorError } from '../../shared/mobmonitor-error';

@Component({
  selector: 'mob-error-display-dialog',
  templateUrl: './error-display-dialog.component.html',
  styleUrls: ['./error-display-dialog.component.scss']
})
export class ErrorDisplayDialogComponent implements OnInit {
  bodyText: string;

  constructor(
    public dialogRef: MatDialogRef<ErrorDisplayDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: MobmonitorError
  ) {}

  ngOnInit() {
    this.bodyText = JSON.stringify(this.data.body);
  }
}
