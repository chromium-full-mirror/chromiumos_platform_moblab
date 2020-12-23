import {Component, EventEmitter, Inject, Input, Output} from '@angular/core';

export enum LoadingOverlayStyle {
  // renders overlay over entirety of the parent component.
  Center = 1,
  // renders overlay at the top of the parent component, as a tag.
  Top,
}

@Component({
  selector: 'app-loading-overlay',
  templateUrl: './loading-overlay.component.html',
  styleUrls: ['./loading-overlay.component.scss'],
})
export class LoadingOverlayComponent {
  @Input() style = LoadingOverlayStyle.Center;

  message = '';
  hideOverlay = true;

  constructor() {}

  isCenterOverlay() {
    return this.style === LoadingOverlayStyle.Center;
  }

  isTopOverlay() {
    return this.style === LoadingOverlayStyle.Top;
  }

  updateStatus(message: string, style: LoadingOverlayStyle = 1): void {
    this.message = message;
    this.setStyle(style);
    this.show();
  }

  setStyle(style: LoadingOverlayStyle): void {
    this.style = style;
  }

  show(): void {
    this.hideOverlay = false;
  }

  hide(): void {
    this.hideOverlay = true;
  }
}
