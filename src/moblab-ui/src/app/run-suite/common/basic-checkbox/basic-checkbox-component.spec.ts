/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import {MatTooltipModule} from '@angular/material/tooltip';

import {BasicInputFormComponent} from './basic-input.component';

describe('BasicInputFormComponent', () => {
  let component: BasicInputFormComponent;
  let fixture: ComponentFixture<BasicInputFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        FormsModule,
        MatFormFieldModule,
        MatInputModule,
        MatTooltipModule,
        ReactiveFormsModule,
      ],
      declarations: [BasicInputFormComponent],
    }).compileComponents();
  }));

  function setInput(inputValue) {
    const inputForm = fixture.debugElement.nativeElement.querySelector(
      '#input'
    );
    inputForm.focus();
    inputForm.value = inputValue;
    inputForm.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  beforeEach(() => {
    fixture = TestBed.createComponent(BasicInputFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('input works.', () => {
    const input_str = 'TestInput';
    setInput(input_str);
    expect(component.getInput()).toBe(input_str);
  });

  it('numeric validator errors non-numbers.', () => {
    component.setNumericValidation();
    setInput('NaN');

    expect(component.getInputFormControl().hasError('isNaN')).toBe(true);
  });

  it('update emitter fires on input change', () => {
    // the input events fired below don't include a 'blur' event, which is fired
    // when the user navigates away from a form.
    setInput('1');

    fixture.whenStable().then(() => {
      expect(component.update.emit).toHaveBeenCalledTimes(1);
    });
  });
});
