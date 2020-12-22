import {Component, EventEmitter, Input, Output} from '@angular/core';

@Component({
  selector: 'app-button-with-progress',
  templateUrl: './button-with-progress.component.html',
  styleUrls: ['./button-with-progress.component.scss'],
})
export class ButtonWithProgressComponent {
  @Input() caption = '';
  @Output() buttonClick = new EventEmitter();
  isLoading = false;

  setIsLoadingStatus(isLoading: boolean) {
    this.isLoading = isLoading;
  }

  onButtonClick(): void {
    this.buttonClick.emit();
  }
}
