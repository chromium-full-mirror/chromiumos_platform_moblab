/* tslint:disable:no-unused-variable */
import { DebugElement } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';

import { FirmwareComponent } from './firmware.component';

import {
  MatCardModule,
  MatCheckboxModule,
  MatTableModule
} from "@angular/material";

describe('FirmwareComponent', () => {
  let component: FirmwareComponent;
  let fixture: ComponentFixture<FirmwareComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
        imports: [MatCardModule, MatCheckboxModule, MatTableModule],
        declarations: [FirmwareComponent]})
        .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FirmwareComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
