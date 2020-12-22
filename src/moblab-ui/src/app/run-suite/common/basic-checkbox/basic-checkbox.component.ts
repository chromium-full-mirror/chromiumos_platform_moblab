import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {FormControl} from '@angular/forms';

import {BaseForm} from '../base-form/base-form.component';

/**
 * Component meant to be used for checkbox form items in run suite components.
 */
@Component({
  selector: 'app-basic-checkbox',
  templateUrl: './basic-checkbox.component.html',
  styleUrls: ['./basic-checkbox.component.css'],
})
export class BasicCheckboxFormComponent extends BaseForm implements OnInit {
  @Input() name: string;
  @Output() update = new EventEmitter();

  private check = new FormControl('');

  ngOnInit(): void {
    this.check.setValue(false);
    this.check.valueChanges.subscribe(value => {
      this.update.emit(this.check.value);
    });
  }

  getChecked() {
    return this.check.value;
  }

  getCheckboxFormControl() {
    return this.check;
  }

  enable() {
    super.enable();
    this.check.enable();
  }

  disable(message?: string) {
    super.disable(message);
    this.check.disable();
  }
}
