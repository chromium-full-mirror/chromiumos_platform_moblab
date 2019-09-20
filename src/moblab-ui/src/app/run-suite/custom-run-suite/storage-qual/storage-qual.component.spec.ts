/* tslint:disable:no-unused-variable */
import {DebugElement} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';

import {StorageQualComponent} from './storage-qual.component';

describe('StorageQualComponent', () => {
  let component: StorageQualComponent;
  let fixture: ComponentFixture<StorageQualComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({declarations: [StorageQualComponent]})
        .compileComponents();
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
