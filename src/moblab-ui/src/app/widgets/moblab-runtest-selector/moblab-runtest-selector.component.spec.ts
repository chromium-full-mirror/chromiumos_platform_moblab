/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed} from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatSelectModule } from "@angular/material/select";

import { MoblabBuildSelectorComponent } from '../moblab-build-selector/moblab-build-selector.component';
import { MoblabRuntestSelectorComponent } from './moblab-runtest-selector.component';
import { MoblabSelectorComponent } from '../moblab-selector/moblab-selector.component';

describe('MoblabRuntestSelectorComponent', () => {
  let component: MoblabRuntestSelectorComponent;
  let fixture: ComponentFixture<MoblabRuntestSelectorComponent>;

  beforeEach(async(() => {
    TestBed
        .configureTestingModule(
            {
              imports: [FormsModule, MatSelectModule],
              declarations: [
                MoblabBuildSelectorComponent,
                MoblabRuntestSelectorComponent,
                MoblabSelectorComponent,
              ]})
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
