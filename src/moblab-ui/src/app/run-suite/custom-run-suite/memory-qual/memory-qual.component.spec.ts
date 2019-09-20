/* tslint:disable:no-unused-variable */
import {DebugElement} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';

import {MemoryQualComponent} from './memory-qual.component';

describe('MemoryQualComponent', () => {
  let component: MemoryQualComponent;
  let fixture: ComponentFixture<MemoryQualComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({declarations: [MemoryQualComponent]})
        .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MemoryQualComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
