/* tslint:disable:no-unused-variable */
import { MatSelectModule } from "@angular/material/select";
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { MoblabSelectorComponent } from './moblab-selector.component';

describe('MoblabSelectorComponent', () => {
  let component: MoblabSelectorComponent;
  let fixture: ComponentFixture<MoblabSelectorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
        imports: [FormsModule, MatSelectModule],
        declarations: [MoblabSelectorComponent]})
        .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MoblabSelectorComponent);
    component = fixture.componentInstance;
    component.options = [];
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
