/* tslint:disable:no-unused-variable */

import { async, TestBed } from '@angular/core/testing';
import {
  MatIconModule,
  MatToolbarModule
} from '@angular/material';
import { NO_ERRORS_SCHEMA } from '@angular/core';

import { AppComponent } from './app.component';

describe('AppComponent', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [MatIconModule, MatToolbarModule],
      declarations: [AppComponent],
      schemas: [NO_ERRORS_SCHEMA]
    });
    TestBed.compileComponents();
  });

  it('should create the app', async(() => {
       const fixture = TestBed.createComponent(AppComponent);
       const app = fixture.componentInstance;
       expect(app).toBeTruthy();
     }));
});
