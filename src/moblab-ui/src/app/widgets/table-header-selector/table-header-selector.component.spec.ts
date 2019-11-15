/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';
import {
  MatCheckboxModule,
  MatSelectModule
} from "@angular/material";


import { TableHeaderSelectorComponent } from './table-header-selector.component';
import { MoblabSelectorComponent } from '../moblab-selector/moblab-selector.component';

describe('TableHeaderSelectorComponent', () => {
  let component: TableHeaderSelectorComponent;
  let fixture: ComponentFixture<TableHeaderSelectorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        FormsModule,
        MatCheckboxModule,
        MatSelectModule,
      ],
      declarations: [ TableHeaderSelectorComponent, MoblabSelectorComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TableHeaderSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
