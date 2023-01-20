/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {MatSnackBarModule} from '@angular/material/snack-bar';
import {FWUPDRunComponent} from './fwupd.component';
import {RouterModule} from '@angular/router';

import {BasicInputFormComponent} from '../common/basic-input-form/basic-input.component';

describe('FWUPDRunComponent', () => {
  let component: FWUPDRunComponent;
  let fixture: ComponentFixture<FWUPDRunComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [MatSnackBarModule, RouterModule, RouterModule.forRoot([])],
      declarations: [BasicInputFormComponent, FWUPDRunComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FWUPDRunComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
