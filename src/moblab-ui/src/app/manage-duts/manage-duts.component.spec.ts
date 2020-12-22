/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {By} from '@angular/platform-browser';
import {DebugElement} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatTableModule} from '@angular/material/table';
import {MatTabsModule} from '@angular/material/tabs';
import {RouterModule} from '@angular/router';

import {EditAttributesComponent} from './edit-attributes/edit-attributes.component';
import {EnrollmentComponent} from './enrollment/enrollment.component';
import {FirmwareComponent} from './firmware/firmware.component';
import {ManageDutsComponent} from './manage-duts.component';
import {ViewDutsComponent} from './view-duts/view-duts.component';
import {WidgetsModule} from 'app/widgets/widgets.module';

import {PipesModule} from 'app/pipes/pipes.module';

describe('ManageDutsComponent', () => {
  let component: ManageDutsComponent;
  let fixture: ComponentFixture<ManageDutsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        FormsModule,
        MatCardModule,
        MatCheckboxModule,
        MatFormFieldModule,
        MatIconModule,
        MatInputModule,
        MatSnackBarModule,
        MatTableModule,
        MatTabsModule,
        PipesModule,
        ReactiveFormsModule,
        RouterModule,
        WidgetsModule,
      ],
      declarations: [
        EditAttributesComponent,
        EnrollmentComponent,
        FirmwareComponent,
        ManageDutsComponent,
        ViewDutsComponent,
      ],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ManageDutsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
