import {Component, Input, Output, EventEmitter, ViewChild} from '@angular/core';

@Component({
  selector: 'moblab-selector',
  template: `
  <div *ngIf="isShown">
      <md-list-item>
      <label class="moblab-selector-label"> {{title}} </label>
      <md-select
       placeholder="{{placeholder}}"
       [(ngModel)]="selectedValue" (ngModelChange)="onChange($event)">>
        <md-option *ngFor="let option of options" [value]="option">{{option}}</md-option>
      </md-select>
      </md-list-item>
  </div>
`,
  styleUrls: ['../app.component.css'],
})

export class MoblabSelector {
  @Input() title: string;
  @Input() placeholder: string;
  @Input() options: string[];
  @Input() isShown: boolean = true;

  @Output() update = new EventEmitter();
  @Output() value: string = null;

  onChange(event) : void {
   console.log(event);
   this.value = event;
   this.update.emit({value:event});
  }

  setVisible(newState) : void {
    this.isShown = newState;
  }

  getSelectedValue() : string {
    if (!this.isShown) {
      return null;
    } else {
      return this.value;
    }
  }
}


