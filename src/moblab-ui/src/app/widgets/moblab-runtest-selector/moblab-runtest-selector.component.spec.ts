/* tslint:disable:no-unused-variable */
import {DebugElement} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';

import {MoblabRuntestSelectorComponent} from './moblab-runtest-selector.component';

describe('MoblabRuntestSelectorComponent', () => {
  let component: MoblabRuntestSelectorComponent;
  let fixture: ComponentFixture<MoblabRuntestSelectorComponent>;

  beforeEach(async(() => {
    TestBed
        .configureTestingModule(
            {declarations: [MoblabRuntestSelectorComponent]})
        .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MoblabRuntestSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
