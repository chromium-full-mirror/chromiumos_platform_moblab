import {Component, OnInit, EventEmitter, Input, Output} from '@angular/core';

export const CHECKBOX_ID = 'inner-checkbox';

@Component({
  selector: 'app-table-header-selector',
  templateUrl: './table-header-selector.component.html',
  styleUrls: ['./table-header-selector.component.scss'],
})
export class TableHeaderSelectorComponent implements OnInit {
  checkboxId = CHECKBOX_ID;
  selectValue: string = undefined;
  checkboxState = false;

  @Input() options: string[];
  @Output() update = new EventEmitter();

  standardOptions = ['All', 'None'];

  constructor() {}

  ngOnInit() {}

  selectionChange() {
    this.update.emit({selection: this.selectValue});
    if (this.selectValue === this.standardOptions[0]) {
      this.checkboxState = true;
    } else if (this.selectValue === this.standardOptions[1]) {
      this.checkboxState = false;
    } else {
      this.checkboxState = true;
    }
    this.selectValue = undefined;
  }

  checkboxChange() {
    this.checkboxState = !this.checkboxState;
    this.update.emit({
      selection: this.checkboxState
        ? this.standardOptions[0]
        : this.standardOptions[1],
    });
  }

  setCheckboxState(checkboxState) {
    this.checkboxState = checkboxState;
  }

  getCheckboxState() {
    return this.checkboxState;
  }
}
