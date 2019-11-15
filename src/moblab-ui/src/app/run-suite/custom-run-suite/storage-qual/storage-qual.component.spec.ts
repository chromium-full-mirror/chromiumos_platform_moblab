/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';
import { MatCardModule } from '@angular/material/card';

import { StorageQualComponent } from './storage-qual.component';
import { WidgetsModule } from "app/widgets/widgets.module";

describe('StorageQualComponent', () => {
  let component: StorageQualComponent;
  let fixture: ComponentFixture<StorageQualComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        MatCardModule,
        WidgetsModule,
      ],
      declarations: [StorageQualComponent]})
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(StorageQualComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
