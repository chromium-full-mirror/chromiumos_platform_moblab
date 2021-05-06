import {
  Component,
  EventEmitter,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';

@Component({
  selector: 'app-run-suite-button',
  template: `
    <button
      #runSuiteButton
      mat-raised-button
      color="primary"
      [disabled]="this.isDisabled()"
      (click)="clicked()"
    >
      Run Suite
    </button>
  `,
  styleUrls: [],
})
/**
 * Component meant to be used at the end of all custom run suite forms.
 */
export class RunSuiteButtonComponent {
  @Output() onClick = new EventEmitter();

  // Default to disabled because suite user generally has to input form items
  // before submission.
  private disabled = true;

  enable() {
    this.disabled = false;
  }

  disable() {
    this.disabled = true;
  }

  clicked() {
    this.onClick.emit();
  }

  isDisabled() {
    return this.disabled;
  }
}
