/* tslint:disable:no-unused-variable */
import {DebugElement} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';

import {RunAnySuiteComponent} from './run-any-suite.component';

describe('RunAnySuiteComponent', () => {
  let component: RunAnySuiteComponent;
  let fixture: ComponentFixture<RunAnySuiteComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({declarations: [RunAnySuiteComponent]})
        .compileComponents();
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
