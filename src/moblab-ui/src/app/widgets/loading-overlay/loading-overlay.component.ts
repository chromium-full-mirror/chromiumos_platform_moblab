import {
  Component,
  EventEmitter,
  Inject,
  Output
} from '@angular/core';

@Component({
  selector: 'app-loading-overlay',
  templateUrl: './loading-overlay.component.html',
  styleUrls: ['./loading-overlay.component.scss'],
})
export class LoadingOverlayComponent{
  message = '';
  hideOverlay = true;

  constructor() {}

  updateStatus(message: string): void {
    this.message = message;
    this.show();
  }

  show(): void {
    this.hideOverlay = false;
  }

  hide(): void {
    this.hideOverlay = true;
  }
}
