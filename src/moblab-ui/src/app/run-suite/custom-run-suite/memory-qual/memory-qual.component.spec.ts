/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {RouterModule} from '@angular/router';

import {BasicInputFormComponent} from '../../common/basic-input-form/basic-input.component';
import {MemoryQualComponent} from './memory-qual.component';

describe('MemoryQualComponent', () => {
  let component: MemoryQualComponent;
  let fixture: ComponentFixture<MemoryQualComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        MatSnackBarModule,
        RouterModule,
        RouterModule.forRoot([]),
      ],
      declarations: [BasicInputFormComponent, MemoryQualComponent],
    }).compileComponents();
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
