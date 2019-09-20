/* tslint:disable:no-unused-variable */
import {DebugElement} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';

import {MoblabSelectorComponent} from './moblab-selector.component';

describe('MoblabSelectorComponent', () => {
  let component: MoblabSelectorComponent;
  let fixture: ComponentFixture<MoblabSelectorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({declarations: [MoblabSelectorComponent]})
        .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MoblabSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
