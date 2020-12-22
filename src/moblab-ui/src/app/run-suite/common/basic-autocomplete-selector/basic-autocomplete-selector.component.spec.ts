/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {Component, DebugElement} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatAutocompleteModule} from '@angular/material/autocomplete';
import {MatCardModule} from '@angular/material/card';
import {MatInputModule} from '@angular/material/input';
import {MatSelectModule} from '@angular/material/select';
import {MatTooltipModule} from '@angular/material/tooltip';

import {BasicAutocompleteSelectorComponent} from './basic-autocomplete-selector.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

const MODULE_IMPORT_DEFINITIONS = [
  BrowserAnimationsModule,
  FormsModule,
  MatAutocompleteModule,
  MatCardModule,
  MatInputModule,
  MatSelectModule,
  MatTooltipModule,
  ReactiveFormsModule,
];

@Component({
  selector: 'basic-autocomplete-wrapper',
  template: `
    <app-basic-autocomplete-selector
      [title]="'Select option:'"
      [placeholder]="['Pick from available options']"
      [options]="['MockOption1', 'MockOption2']"
      [isShown]="true"
      (update)="selectChanged($event.value)"
    >
    </app-basic-autocomplete-selector>
  `,
})
class BasicAutocompleteWrapperComponent {
  selectChanged(event) {}
}

describe('tests on autocomplete selector', () => {
  let component: BasicAutocompleteSelectorComponent;
  let fixture: ComponentFixture<BasicAutocompleteWrapperComponent>;

  function fireEvent(identifier: string, event: string) {
    const inputEl = fixture.debugElement.nativeElement.querySelector(
      '#' + identifier
    );
    inputEl.dispatchEvent(new Event(event));
    fixture.detectChanges();
  }

  function fireInputEvent(inputIdentifier: string, input: string) {
    const inputEl = fixture.debugElement.nativeElement.querySelector(
      '#' + inputIdentifier
    );
    inputEl.value = input;
    inputEl.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: MODULE_IMPORT_DEFINITIONS,
      declarations: [
        BasicAutocompleteSelectorComponent,
        BasicAutocompleteWrapperComponent,
      ],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BasicAutocompleteWrapperComponent);
    component = fixture.debugElement.children[0].componentInstance;
    spyOn(component.select, 'emit');
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('check input and select registers', () => {
    fireInputEvent('autocompleteInput', 'MockOption1');
    expect(component.getSelectedValue()).toBe('MockOption1');
  });

  it('check ambiguous input will not select', () => {
    fireInputEvent('autocompleteInput', 'MockOption');
    expect(component.getSelectedValue()).toBe('');
  });

  it('check non-matching input will not select', () => {
    fireInputEvent('autocompleteInput', 'MockOption3');
    expect(component.getSelectedValue()).toBe('');
  });

  it('check that selected and then changed input will update', () => {
    fireInputEvent('autocompleteInput', 'MockOption1');
    fireEvent('autocomplete-wrapper', 'focus');
    fireInputEvent('autocompleteInput', 'MockOption2');
    expect(component.getSelectedValue()).toBe('MockOption2');
  });

  it('check that focus and no change will not change selected value', () => {
    fireInputEvent('autocompleteInput', 'MockOption1');
    fireEvent('autocomplete-wrapper', 'focus');
    fireEvent('autocomplete-wrapper', 'blur');
    expect(component.getSelectedValue()).toBe('MockOption1');
  });

  it('check that focus and bad change will clear selected value', () => {
    fireInputEvent('autocompleteInput', 'MockOption1');
    fireEvent('autocomplete-wrapper', 'focus');
    fireInputEvent('autocompleteInput', 'MockOption3');
    expect(component.getSelectedValue()).toBe('');
  });
});

@Component({
  selector: 'basic-autocomplete-single-option-wrapper',
  template: `
    <app-basic-autocomplete-selector
      [title]="'Select option:'"
      [placeholder]="['Pick from available options']"
      [options]="['MockOption1']"
      [isShown]="true"
      (update)="selectChanged($event.value)"
    >
    </app-basic-autocomplete-selector>
  `,
})
class BasicAutocompleteSingleOptionWrapperComponent {
  selectChanged(event) {}
}

describe('tests on single-option autocomplete selector', () => {
  let component: BasicAutocompleteSelectorComponent;
  let wrapperFixture: ComponentFixture<BasicAutocompleteSingleOptionWrapperComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: MODULE_IMPORT_DEFINITIONS,
      declarations: [
        BasicAutocompleteSelectorComponent,
        BasicAutocompleteSingleOptionWrapperComponent,
      ],
    }).compileComponents();
  }));

  beforeEach(() => {
    wrapperFixture = TestBed.createComponent(
      BasicAutocompleteSingleOptionWrapperComponent
    );
    component = wrapperFixture.debugElement.children[0].componentInstance;
    wrapperFixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('one option selector autocompletes.', () => {
    expect(component.getSelectedValue()).toBe('MockOption1');
  });
});
