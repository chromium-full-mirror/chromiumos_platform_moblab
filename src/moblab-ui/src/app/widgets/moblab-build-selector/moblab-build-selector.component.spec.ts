/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatSelectModule } from "@angular/material/select";

import { MoblabBuildSelectorComponent } from './moblab-build-selector.component';
import { MoblabSelectorComponent } from '../moblab-selector/moblab-selector.component';

describe('MoblabBuildSelectorComponent', () => {
  let component: MoblabBuildSelectorComponent;
  let fixture: ComponentFixture<MoblabBuildSelectorComponent>;

  beforeEach(async(() => {
    TestBed
        .configureTestingModule({
          imports: [FormsModule, MatSelectModule],
          declarations: [MoblabBuildSelectorComponent, MoblabSelectorComponent]})
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
