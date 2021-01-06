/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {MatSnackBarModule} from '@angular/material/snack-bar';
import {RouterModule} from '@angular/router';

import {BasicInputFormComponent} from '../../common/basic-input-form/basic-input.component';
import {StorageQualV2Component} from './storage-qual-v2.component';

describe('StorageQualV2Component', () => {
  let component: StorageQualV2Component;
  let fixture: ComponentFixture<StorageQualV2Component>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [MatSnackBarModule, RouterModule, RouterModule.forRoot([])],
      declarations: [BasicInputFormComponent, StorageQualV2Component],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(StorageQualV2Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  // ToDo: Fix this test chromium:1163700
  xit('should create', () => {
    expect(component).toBeTruthy();
  });
});
