/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {MatSnackBarModule} from '@angular/material/snack-bar';
import {RouterModule} from '@angular/router';

import {BasicInputFormComponent} from '../../common/basic-input-form/basic-input.component';
import {PvsComponent} from './pvs.component';

describe('PvsComponent', () => {
  let component: PvsComponent;
  let fixture: ComponentFixture<PvsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [MatSnackBarModule, RouterModule, RouterModule.forRoot([])],
      declarations: [BasicInputFormComponent, PvsComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PvsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
