import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {FormControl} from '@angular/forms';

import {BaseForm} from '../base-form/base-form.component';
import {numericValidator} from '../../../utils/validators';

/**
 * Component meant to be used for input form items in run suite components.
 */
@Component({
  selector: 'app-basic-input',
  templateUrl: './basic-input.component.html',
  styleUrls: ['./basic-input.component.css'],
})
export class BasicInputFormComponent extends BaseForm implements OnInit {
  @Input() name: string;
  @Input() isNumeric: boolean;
  @Output() update = new EventEmitter();

  private input = new FormControl('');

  ngOnInit(): void {
    if (this.isNumeric) {
      this.setNumericValidation();
    }

    this.input.valueChanges.subscribe(value => {
      this.update.emit(this.input.value);
    });
  }

  setNumericValidation() {
    this.input.setValidators([numericValidator]);
  }

  getInput() {
    return this.input.value;
  }

  clear() {
    this.input.reset();
  }

  getInputFormControl() {
    return this.input;
  }

  enable() {
    super.enable();
    this.input.enable({ emitEvent: false });
  }

  disable(message?: string) {
    super.disable(message);
    this.input.disable();
  }
}
