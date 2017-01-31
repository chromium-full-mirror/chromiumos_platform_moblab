import {Component, Input, Output, EventEmitter, ViewChild} from '@angular/core';

@Component({
  selector: 'moblab-selector',
  template: `
  <div>
    {{title}}
    <select disabled
       #sel
      (change)="update.emit({value:sel.value, index:sel.selectedIndex})">
      <option *ngFor="let option of options" 
          value="{{option}}">{{option}}
       </option>
    </select>
  </div>
`,
  styleUrls: ['../app.component.css'],
})

export class MoblabSelector {
  @Input() title: string;
  @Input() options: string[];

  @Output() update = new EventEmitter();

  @ViewChild('sel', ) selector;

  setDisabled(newState) : void {
    this.selector.nativeElement.disabled=newState;
  }

  getSelectedValue() : string {
    if (this.selector.nativeElement.selectedIndex == 0) {
      return null;
    } else {
      return this.selector.nativeElement.options[this.selector.nativeElement.selectedIndex].text;
    }
  }
}


