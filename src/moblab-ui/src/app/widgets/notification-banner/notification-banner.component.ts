import {Component, EventEmitter, Input, Output} from '@angular/core';
import {Notification, NotificationType} from '../../services/notifications.service';

@Component({
  selector: 'app-notification-banner',
  templateUrl: './notification-banner.component.html',
  styleUrls: ['./notification-banner.component.scss'],
})
export class NotificationBannerComponent {
  @Input() notification: Notification;
  @Output() dismissClick = new EventEmitter<Notification>();

  constructor() { }

  onDismissClicked(): void {
    this.dismissClick.emit(this.notification);
  }

  getCssClass() {
    if (this.notification.type === NotificationType.Error) {
      return "error-notification";
    }
    return "info-notification";
  }

  isDismissable() {
    return this.notification.type === NotificationType.Error;
  }
}
