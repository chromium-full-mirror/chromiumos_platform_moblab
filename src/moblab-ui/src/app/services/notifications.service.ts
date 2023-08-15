import {Injectable} from '@angular/core';
import {BehaviorSubject, Observable, timer} from 'rxjs';
import {v4 as uuidv4} from 'uuid';

export enum NotificationType {
  Info,
  Error,
}

export class Notification {
  constructor(
    public message: string,
    public type: NotificationType = NotificationType.Info,
    public id: string = uuidv4()
  ) {}
}

@Injectable({providedIn: 'root'})
export class NotificationsService {
  public notificationsObservable: Observable<Notification[]>;
  private notifications: Notification[] = [];
  private notificationsSubject = new BehaviorSubject(this.notifications);

  constructor() {
    this.notificationsObservable = this.notificationsSubject.asObservable();
  }

  public notify(message: string) {
    const notification = new Notification(message, NotificationType.Info);
    this.notifications.push(notification);
    this.pushNotificationsUpdate();
    this.hideInfoMessage(notification.id);
  }

  public error(error: unknown) {
    let notification = null;
    if (typeof error === 'string') {
      notification = new Notification(error, NotificationType.Error);
    } else if (typeof error === 'object' && 'message' in error && typeof error.message === 'string') {
      notification = new Notification(error.message, NotificationType.Error);
    }

    if (notification) {
      this.notifications.push(notification);
      this.pushNotificationsUpdate();
    }
  }

  public dismiss(id: string) {
    this.notifications = this.notifications.filter(n => n.id !== id);
    this.pushNotificationsUpdate();
  }

  private pushNotificationsUpdate() {
    this.notificationsSubject.next(this.notifications);
  }

  private hideInfoMessage(id: string) {
    timer(5000).subscribe(_ => this.dismiss(id));
  }
}
