/* tslint:disable:no-unused-variable */
import {DebugElement} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';

import {MoblabBuildSelectorComponent} from './moblab-build-selector.component';

describe('MoblabBuildSelectorComponent', () => {
  let component: MoblabBuildSelectorComponent;
  let fixture: ComponentFixture<MoblabBuildSelectorComponent>;

  beforeEach(async(() => {
    TestBed
        .configureTestingModule({declarations: [MoblabBuildSelectorComponent]})
        .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MoblabBuildSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
