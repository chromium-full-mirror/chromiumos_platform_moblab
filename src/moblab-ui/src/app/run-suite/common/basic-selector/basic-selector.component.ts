import {
  Component,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChange,
  SimpleChanges,
} from '@angular/core';

import {BaseForm} from '../base-form/base-form.component';


/**
 * Selector to be used in run suite forms. Contains logic that should be
 * commonly used across suite forms (e.g., autoselect).
 */
@Component({
  selector: 'app-basic-selector',
  templateUrl: './basic-selector.component.html',
  styleUrls: ['./basic-selector.component.scss'],
})
export class BasicSelectorComponent extends BaseForm implements OnChanges, OnInit {
  @Input() autoselect = true;
  @Input() options: string[];
  @Input() placeholder: string;
  @Input() title: string;

  @Output() selected: string = null;

  ngOnInit() {
    this.autoSelectedSingleOption();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes.options) {
      this.options = changes.options.currentValue;
      this.autoSelectedSingleOption();
    }
  }

  autoSelectedSingleOption() {
    // If the drop down only has one item - auto select it.
    if (this.autoselect && this.options.length === 1) {
      this.selected = this.options[0];
      this.update.emit({value: this.selected});
    }
  }

  onChange(event: Event): void {
    this.update.emit(event);
  }

  getSelectedValue(): string {
    return !this.isShown ? null : this.selected;
  }
}
