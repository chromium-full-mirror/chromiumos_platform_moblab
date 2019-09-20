/* tslint:disable:no-unused-variable */
import {DebugElement} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';

import {ManageDutsComponent} from './manage-duts.component';

describe('ManageDutsComponent', () => {
  let component: ManageDutsComponent;
  let fixture: ComponentFixture<ManageDutsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({declarations: [ManageDutsComponent]})
        .compileComponents();
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
