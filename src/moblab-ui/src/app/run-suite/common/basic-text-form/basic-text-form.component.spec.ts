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
        declarations: [
          BasicTextFormComponent,
        ]})
      .compileComponents();
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

  it('Basic input test.', () => {
    const modules_list_str = 'MockModule1, MockModule2';
    setInput(modules_list_str);
    expect(component.getText()).toBe(modules_list_str);
  });
});
