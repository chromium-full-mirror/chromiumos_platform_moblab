/* tslint:disable:no-unused-variable */
import { DebugElement } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {
  MatCardModule,
  MatCheckboxModule,
  MatTableModule,
  MatTabsModule
} from "@angular/material";

import { EnrollmentComponent } from './enrollment/enrollment.component';
import { FirmwareComponent } from './firmware/firmware.component';
import { ManageDutsComponent } from './manage-duts.component';
import { PipesModule } from "app/pipes/pipes.module";
import { WidgetsModule } from "app/widgets/widgets.module";

describe('ManageDutsComponent', () => {
  let component: ManageDutsComponent;
  let fixture: ComponentFixture<ManageDutsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        MatCardModule,
        MatCheckboxModule,
        MatTableModule,
        MatTabsModule,
        PipesModule,
        WidgetsModule
      ],
        declarations: [ManageDutsComponent, FirmwareComponent, EnrollmentComponent]})
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
