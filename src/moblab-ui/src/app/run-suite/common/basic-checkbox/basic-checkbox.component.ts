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

  checkForm = new FormControl(false);

  ngOnInit(): void {
    this.checkForm.setValue(false);
    this.checkForm.disable();
    this.checkForm.valueChanges.subscribe(value => {
      this.update.emit(this.checkForm.value);
    });
  }

  getChecked() {
    return this.checkForm.value;
  }

  enable() {
    super.enable();
    this.checkForm.enable();
  }

  disable(message?: string) {
    super.disable(message);
    this.checkForm.disable();
  }
}
