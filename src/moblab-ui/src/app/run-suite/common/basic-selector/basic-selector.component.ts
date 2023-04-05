import {
  Component,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
  ViewChild,
} from '@angular/core';

import {BaseForm} from '../base-form/base-form.component';
import {EventEmitter} from '@angular/core';
import {MatSelect, MatSelectChange} from '@angular/material/select';
import {SelectableItem} from '../basic-autocomplete-selector/basic-autocomplete-selector.component';

/**
 * Selector to be used in run suite forms. Contains logic that should be
 * commonly used across suite forms (e.g., autoselect).
 */
@Component({
  selector: 'app-basic-selector',
  templateUrl: './basic-selector.component.html',
  styleUrls: ['./basic-selector.component.scss'],
})
export class BasicSelectorComponent
  extends BaseForm
  implements OnChanges, OnInit {
  @ViewChild(MatSelect) selector: MatSelect;

  @Input() autoselect = true;
  @Input() options: SelectableItem[] | string[] = [];
  @Input() placeholder = '';
  @Input() title = '';
  @Input() recommendedBuild = false;

  @Output() select = new EventEmitter();

  selected: string = '';
  selectableItems: SelectableItem[] = [];

  ngOnInit() {
    this.autoSelectedSingleOption();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes.options) {
      this.options = changes.options.currentValue;
      this.parseOptionsToSelectableItems();
      this.autoSelectedSingleOption();
    }
  }

  parseOptionsToSelectableItems() {
    if (Array.isArray(this.options) && this.options.length >= 1) {
        if (this.options[0] instanceof SelectableItem) {
            this.selectableItems = this.options as SelectableItem[];
        }
        else if (typeof this.options[0] === 'string'){
            this.selectableItems = (this.options as string[]).map(e => new SelectableItem(e));
        }
    }
  }

  clearSelection() {
    this.selected = '';
    this.selector?.writeValue(null);
  }

  autoSelectedSingleOption() {
    // If the drop down only has one item - auto select it.
    if (this.autoselect && this.selectableItems.length === 1) {
      this.selected = this.selectableItems[0].text;
      this.select.emit({value: this.selected});
    }
  }

  onChange(event: MatSelectChange): void {
    this.select.emit(event);
  }

  updateStatus(status): void {
    this.recommendedBuild = status == 'Recommended';
  }

  selectOption(optionIndex) {
    if (optionIndex >= 0 && optionIndex < this.selectableItems.length) {
      this.selected = this.selectableItems[optionIndex].text;
      this.select.emit({value: this.selected});
    }
  }
}
