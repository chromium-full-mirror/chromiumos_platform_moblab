import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import {
  Notification,
  NotificationType,
} from '../../services/notifications.service';

@Component({
  selector: 'app-notification-banner',
  templateUrl: './notification-banner.component.html',
  styleUrls: ['./notification-banner.component.scss'],
})
export class NotificationBannerComponent implements OnInit {
  @Input() notification: Notification;
  @Output() dismissClick = new EventEmitter<Notification>();

  cssClasses = 'info-notification'
  isBtnDisabled = false;

  constructor() { }

  ngOnInit() {
    if (this.notification.type === NotificationType.Error) {
      this.cssClasses = 'error-notification';
      this.isBtnDisabled = this.notification.type === NotificationType.Error;
    }
  }

  onDismissClicked(): void {
    this.dismissClick.emit(this.notification);
  }
}
