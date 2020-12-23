import {Component, EventEmitter, Input, Output} from '@angular/core';

const DISABLED_NAME = 'This form is disabled.';

/**
 * Class meant to parent all custom form items for suite runs. (e.g., selectors
 *  input forms, etc ).
 */

@Component({template: ''})
export abstract class BaseForm {
  @Input() isShown: boolean;

  private disabled = false;
  private disabledReasonMessage = DISABLED_NAME;

  constructor() {}

  enable() {
    this.disabled = false;
    this.disabledReasonMessage = '';
  }

  disable(message?: string) {
    this.disabled = true;
    this.disabledReasonMessage = message ? message : DISABLED_NAME;
  }

  getDisabledReason() {
    return this.disabledReasonMessage;
  }

  isDisabled() {
    return this.disabled;
  }
}
