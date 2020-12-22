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
  @ViewChild(MatSelect) selector;

  @Input() autoselect = true;
  @Input() options: string[];
  @Input() placeholder: string;
  @Input() title: string;

  @Output() select = new EventEmitter();

  selected: string = null;

  ngOnInit() {
    this.autoSelectedSingleOption();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes.options) {
      this.options = changes.options.currentValue;
      this.autoSelectedSingleOption();
    }
  }

  clearSelection() {
    this.selected = undefined;
    this.selector.writeValue(null);
  }

  autoSelectedSingleOption() {
    // If the drop down only has one item - auto select it.
    if (this.autoselect && this.options.length === 1) {
      this.selected = this.options[0];
      this.select.emit({value: this.selected});
    }
  }

  onChange(event: MatSelectChange): void {
    this.select.emit(event);
  }

  getSelectedValue(): string {
    return !this.isShown ? null : this.selected;
  }

  selectOption(optionIndex) {
    if (optionIndex >= 0 && optionIndex < this.options.length) {
      this.selected = this.options[optionIndex];
      this.select.emit({value: this.selected});
    }
  }
}
