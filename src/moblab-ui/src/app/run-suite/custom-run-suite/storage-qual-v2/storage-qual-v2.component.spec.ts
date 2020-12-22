/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {MatSnackBarModule} from '@angular/material/snack-bar';
import {RouterModule} from '@angular/router';

import {BasicInputFormComponent} from '../../common/basic-input-form/basic-input.component';
import {StorageQualV2Component} from './storage-qual-v2.component';

describe('StorageQualV2Component', () => {
  let component: StorageQualComponent;
  let fixture: ComponentFixture<StorageQualComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [MatSnackBarModule, RouterModule, RouterModule.forRoot([])],
      declarations: [BasicInputFormComponent, StorageQualComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(StorageQualComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
