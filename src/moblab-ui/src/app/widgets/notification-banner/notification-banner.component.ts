import {Component, Injectable, OnInit} from '@angular/core';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-notification-banner',
  template: '',
})
export class NotificationBannerComponent implements OnInit {
  //TODO(b/188579413): add support for multiple messages on the screen
  constructor(public snackBar: MatSnackBar) { }

  ngOnInit(): void { }

  public notify(message: string) {
    const snackBarRef = this.snackBar.open(message, '', {
      duration: 5000,
      verticalPosition: 'top',
    });
  }

  public error(message: string) {
    const snackBarRef = this.snackBar.open(message, 'Dismiss', {
      verticalPosition: 'top',
      panelClass: ['snack-error'],
    });
  }
}
