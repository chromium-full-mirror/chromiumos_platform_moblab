import {Component, EventEmitter, Output} from '@angular/core';
import {FormControl} from '@angular/forms';
import {BaseForm} from '../base-form/base-form.component';

@Component({
  selector: 'app-basic-text-form',
  templateUrl: './basic-text-form.component.html',
  styleUrls: ['./basic-text-form.component.scss'],
})
/**
 * Component meant to be used for text form items in run suite components.
 * This is a more long-form alternative to input forms.
 */
export class BasicTextFormComponent extends BaseForm {
  @Output() update = new EventEmitter();

  private text = new FormControl('');

  getText() {
    return this.text.value;
  }

  getCsvList() {
    const csv_list = [];
    for (const value of this.getText().split(',')) {
      if (value) {
        csv_list.push(value);
      }
    }
    return csv_list;
  }

  getTextFormControl() {
    return this.text;
  }

  clear() {
    this.text.setValue('');
  }

  enable() {
    super.enable();
    this.text.enable();
  }

  disable(message?: string) {
    super.disable(message);
    this.text.disable();
  }
}
