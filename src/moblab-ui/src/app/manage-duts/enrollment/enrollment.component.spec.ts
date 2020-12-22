/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {By} from '@angular/platform-browser';
import {DebugElement} from '@angular/core';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatIconModule} from '@angular/material/icon';
import {MatTableModule} from '@angular/material/table';
import {RouterModule} from '@angular/router';

import {EnrollmentComponent} from './enrollment.component';
import {PipesModule} from 'app/pipes/pipes.module';
import {WidgetsModule} from 'app/widgets/widgets.module';
import {ViewDutsComponent} from '../view-duts/view-duts.component';
import {MatSnackBarModule} from '@angular/material/snack-bar';

describe('EnrollmentComponent', () => {
  let component: EnrollmentComponent;
  let fixture: ComponentFixture<EnrollmentComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        MatCardModule,
        MatCheckboxModule,
        MatIconModule,
        MatSnackBarModule,
        MatTableModule,
        PipesModule,
        RouterModule,
        RouterModule.forRoot([]),
        WidgetsModule,
      ],
      declarations: [EnrollmentComponent, ViewDutsComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EnrollmentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
