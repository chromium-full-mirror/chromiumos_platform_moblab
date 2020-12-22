/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';
import {DebugElement} from '@angular/core';
import {MatCardModule} from '@angular/material/card';

import {MobmonitorComponent, MobmonitorPipe} from './mobmonitor.component';

describe('MobmonitorComponent', () => {
  let component: MobmonitorComponent;
  let fixture: ComponentFixture<MobmonitorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [MatCardModule],
      declarations: [MobmonitorComponent, MobmonitorPipe],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MobmonitorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
