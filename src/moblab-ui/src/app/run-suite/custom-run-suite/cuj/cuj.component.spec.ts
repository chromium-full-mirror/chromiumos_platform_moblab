/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {BasicAutocompleteSelectorComponent} from '../../common/basic-autocomplete-selector/basic-autocomplete-selector.component';
import {BasicInputFormComponent} from '../../common/basic-input-form/basic-input.component';
import {BasicSelectorComponent} from '../../common/basic-selector/basic-selector.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {BuildSelectFormsComponent} from '../../common/build-select-forms/build-select-forms.component';
import {CUJRunComponent} from './cuj.component';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatAutocompleteModule} from '@angular/material/autocomplete';
import {MatCardModule} from '@angular/material/card';
import {MatInputModule} from '@angular/material/input';
import {MatSelectModule} from '@angular/material/select';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatTooltipModule} from '@angular/material/tooltip';
import {RouterModule} from '@angular/router';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';

describe('CUJRunComponent', () => {
  let component: CUJRunComponent;
  let fixture: ComponentFixture<CUJRunComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        FormsModule,
        MatAutocompleteModule,
        MatCardModule,
        MatInputModule,
        MatSelectModule,
        MatSnackBarModule,
        MatTooltipModule,
        ReactiveFormsModule,
        RouterModule,
        RouterModule.forRoot([]),
      ],
      declarations: [
        BasicAutocompleteSelectorComponent,
        BasicInputFormComponent,
        BasicSelectorComponent,
        BuildSelectFormsComponent,
        CUJRunComponent,
        RunSuiteButtonComponent,
      ],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CUJRunComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
