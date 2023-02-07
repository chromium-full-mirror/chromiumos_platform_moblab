import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  Output,
  SimpleChanges,
} from '@angular/core';

import {BaseForm} from '../base-form/base-form.component';
import {FormControl} from '@angular/forms';
import {MatAutocompleteSelectedEvent} from '@angular/material/autocomplete';
import {Observable} from 'rxjs';
import {map, startWith} from 'rxjs/operators';

export class SelectableItem {
  constructor(public text: string, public status: string = '', public value: string | null = null) {}
}

/**
 * Autocomplete selector to be used in run suite forms.
 */
@Component({
  selector: 'app-basic-autocomplete-selector',
  templateUrl: './basic-autocomplete-selector.component.html',
  styleUrls: ['./basic-autocomplete-selector.component.scss'],
})
export class BasicAutocompleteSelectorComponent
  extends BaseForm
  implements OnChanges {
  // i.e., if only one option is available, select it.
  @Input() autoselect = true;
  @Input() options: SelectableItem[];
  @Input() placeholder: string;
  @Input() title: string;

  @Output() select = new EventEmitter();
  @Output() unselect = new EventEmitter();

  private errorMsg = '';
  private optionSelected = false;
  selectFormControl = new FormControl();
  private selectValueOnUnlock = '';

  filteredOptions: Observable<SelectableItem[]>;

  // Sets up the subscription to the input form control which generates the
  // filtered options dropdown.
  private setFilterOptions() {
    this.filteredOptions = this.selectFormControl.valueChanges.pipe(
      startWith(''),
      map(value => this.getFilteredOptions(value))
    );
  }

  private getFilteredOptions(value: string): SelectableItem[] {
    const filterResults = this.options;
    // if (value) {
    //   value = value.toLowerCase();
    //   filterResults = this.options.filter(option => option.toLowerCase().includes(value));
    // }

    // if (this.options.length && filterResults.length === 0) {
    //   this.setError("Input does not match with any options.");
    // } else if (filterResults.length !== 0) {
    //   this.clearError();
    // }

    return filterResults;
  }

  // If only one option is available, it is automatically selected.
  autoSelectedSingleOption() {
    if (this.autoselect && this.options.filter(o => o.text).length === 1) {
      this.selectFormControl.setValue(this.options.filter(o => o.text)[0].text);
      this.lock();
      this.select.emit({value: this.selectFormControl.value});
    }
  }

  _keyUp(event: any) {
    event.preventDefault();
  }

  onClick() {
    if (this.isLocked() && !this.isDisabled()) {
      this.unlock();
    }
  }

  onOptionSelect(event: MatAutocompleteSelectedEvent) {
    this.selectFormControl.setValue(event.option.value.text);
    this.lock();
  }

  onBlur() {
    if (
      this.isExactMatchToOption() &&
      this.selectFormControl.value !== this.selectValueOnUnlock
    ) {
      this.select.emit({value: this.selectFormControl.value});
      this.lock();
    } else if (this.selectFormControl.value !== this.selectValueOnUnlock) {
      this.unselect.emit();
      this.selectValueOnUnlock = '';
    }
  }

  isExactMatchToOption() {
    return (
      this.options.findIndex(e => e.text === this.selectFormControl.value) !==
      -1
    );
  }

  isNextUp() {
    return !this.selectFormControl.disabled && !this.selectFormControl.value;
  }

  enable() {
    super.enable();
    this.selectFormControl.enable();
  }

  isLocked() {
    return this.optionSelected;
  }

  lock() {
    this.selectFormControl.disable();
    this.optionSelected = true;
  }

  unlock() {
    this.selectFormControl.enable();
    this.optionSelected = false;
    this.selectValueOnUnlock = this.selectFormControl.value;
  }

  disable(message?: string) {
    super.disable(message);
    this.selectFormControl.disable();
  }

  private setError(message: string) {
    if (!this.isDisabled()) {
      this.errorMsg = message;
    }
  }

  clearError() {
    this.errorMsg = '';
  }

  hasError() {
    return this.errorMsg;
  }

  clearSelection() {
    this.clearError();
    this.selectFormControl.setValue('');
  }

  // Tracks changes in options Input
  ngOnChanges(changes: SimpleChanges) {
    if (changes.options) {
      this.options = changes.options.currentValue;
      this.setFilterOptions();
      this.autoSelectedSingleOption();
    }
  }
}
