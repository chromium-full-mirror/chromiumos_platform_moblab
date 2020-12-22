/* tslint:disable:no-unused-variable */
import {DebugElement} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';

import {BvtComponent} from './bvt.component';

describe('BvtComponent', () => {
  let component: BvtComponent;
  let fixture: ComponentFixture<BvtComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [BvtComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BvtComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
