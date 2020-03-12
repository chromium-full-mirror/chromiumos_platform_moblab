import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { ErrorDisplayDialogComponent } from './error-display-dialog/error-display-dialog.component';
import { MobmonitorError } from '../shared/mobmonitor-error';

@Injectable()
export class ErrorDisplayService {
  constructor(public dialog: MatDialog) {}

  /**
   * Opens a helpful dialog describing the error you just encountered
   *
   * @param error MobmonitorError that will be used to construct the dialog
   * if you need a MobmonitorError, use mobmonitor-error.wrapError to construct
   * one
   */
  openErrorDialog(error: MobmonitorError): void {
    this.dialog.open(ErrorDisplayDialogComponent, {
      width: '700px',
      data: error
    });
  }
}
