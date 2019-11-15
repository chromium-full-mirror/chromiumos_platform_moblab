/* tslint:disable:no-unused-variable */
import {DebugElement} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';

import {
  MatCardModule,
  MatCheckboxModule,
  MatTableModule
} from "@angular/material";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { EnrollmentComponent } from './enrollment.component';
import { PipesModule } from "app/pipes/pipes.module";
import { WidgetsModule } from "app/widgets/widgets.module";

describe('EnrollmentComponent', () => {
  let component: EnrollmentComponent;
  let fixture: ComponentFixture<EnrollmentComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
        imports: [
          BrowserAnimationsModule,
          MatCardModule,
          MatCheckboxModule,
          MatTableModule,
          PipesModule,
          WidgetsModule,
        ],
        declarations: [EnrollmentComponent]})
        .compileComponents();
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
