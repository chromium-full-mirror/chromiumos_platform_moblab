/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {MatSnackBarModule} from '@angular/material/snack-bar';
import {RunAnySuiteComponent} from './run-any-suite.component';
import {RouterModule} from '@angular/router';

import {BasicInputFormComponent} from '../common/basic-input-form/basic-input.component';

describe('RunAnySuiteComponent', () => {
  let component: RunAnySuiteComponent;
  let fixture: ComponentFixture<RunAnySuiteComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [MatSnackBarModule, RouterModule, RouterModule.forRoot([])],
      declarations: [BasicInputFormComponent, RunAnySuiteComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RunAnySuiteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
