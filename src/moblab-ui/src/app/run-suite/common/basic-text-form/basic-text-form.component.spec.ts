/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatTooltipModule} from '@angular/material/tooltip';

import {BasicTextFormComponent} from './basic-text-form.component';

describe('BasicTextFormComponent', () => {
  let component: BasicTextFormComponent;
  let fixture: ComponentFixture<BasicTextFormComponent>;

  const MOCK_MODULE_1 = 'MockModule1';
  const MOCK_MODULE_2 = 'MockModule2';
  const MODULES_LIST_STR = MOCK_MODULE_1 + ',' + MOCK_MODULE_2;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        FormsModule,
        MatFormFieldModule,
        MatIconModule,
        MatInputModule,
        MatTooltipModule,
        ReactiveFormsModule,
      ],
      declarations: [BasicTextFormComponent],
    }).compileComponents();
  }));

  function setInput(inputValue) {
    const inputForm = fixture.debugElement.nativeElement.querySelector(
      '#textInput'
    );
    inputForm.value = inputValue;
    inputForm.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  beforeEach(() => {
    fixture = TestBed.createComponent(BasicTextFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should pass through input str', () => {
    setInput(MODULES_LIST_STR);
    expect(component.getText()).toBe(MODULES_LIST_STR);
  });

  it('should parse input str into CSV list', () => {
    setInput(MODULES_LIST_STR);
    expect(component.getCsvList().toString()).toBe(
      [MOCK_MODULE_1, MOCK_MODULE_2].toString()
    );
  });

  it('should parse no-comma input str into 1-item list', () => {
    setInput(MOCK_MODULE_1);
    expect(component.getCsvList().toString()).toBe([MOCK_MODULE_1].toString());
  });

  it('should parse empty input str into 0-item list', () => {
    setInput('');
    expect(component.getCsvList().toString()).toBe([].toString());
  });
});
