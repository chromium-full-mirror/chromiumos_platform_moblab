import {Directive, HostListener, Input} from '@angular/core';
import {MatDialog} from '@angular/material/dialog';
import {NewUpdateDialogComponent} from './new-update-dialog/new-update-dialog.component';
import {NewUpdateStatus} from '../../constants';
import {Overlay} from '@angular/cdk/overlay';

@Directive({selector: '[new-update]'})
export class NewUpdateDirective {
  private overlay: Overlay;

  public constructor(private dialogRef: MatDialog, overlay: Overlay) {
    this.overlay = overlay;
  }

  @HostListener('click')
  public onClick() {
    this.openNewUpdateDialog();
  }

  public openNewUpdateDialog() {
    const dialogRef = this.dialogRef.open(NewUpdateDialogComponent, {
      panelClass: 'c-new-update-dialog',
      backdropClass: 'c-dialog-backdrop',
      disableClose: true,
      height: 'auto',
      width: 'auto',
      scrollStrategy: this.overlay.scrollStrategies.reposition(),
    });
  }
}
