import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { ActionsParamDialogComponent } from './actions-param-dialog.component';

// tslint:disable-next-line
@Component({selector: 'mat-dialog-content', template: '<ng-content></ng-content>'})
class MatDialogStubComponent {}

// tslint:disable-next-line
@Component({selector: 'mat-form-field', template: '<ng-content></ng-content>'})
class MatFormFieldStubComponent {}

// tslint:disable-next-line
@Component({selector: 'mat-error', template: '<ng-content></ng-content>'})
class MatErrorStubComponent {}

// tslint:disable-next-line
@Component({selector: 'mat-dialog-actions', template: '<ng-content></ng-content>'})
class MatDialogActionsSubComponent {}

describe('ActionsParamDialogComponent', () => {
  let component: ActionsParamDialogComponent;
  let fixture: ComponentFixture<ActionsParamDialogComponent>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<ActionsParamDialogComponent>>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        ActionsParamDialogComponent,
        MatDialogStubComponent,
        MatFormFieldStubComponent,
        MatErrorStubComponent,
        MatDialogActionsSubComponent
      ],
      imports : [
        FormsModule
      ],
      providers: [
        {
          provide: MatDialogRef,
          useValue: jasmine.createSpyObj('MatDialogRef', ['close'])
        },
        {
          provide: MAT_DIALOG_DATA,
          useValue: {params: {param1: 'value1'}}
        }
      ]
    })
    .compileComponents();

    dialogRefSpy = TestBed.get(MatDialogRef);
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ActionsParamDialogComponent);
    component = fixture.componentInstance;
    component.ngOnInit();
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should close', () => {
    component.onNoClick();
    expect(dialogRefSpy.close).toHaveBeenCalled();
  });

  it('should accept parameters', () => {
    component.runAction();
    expect(dialogRefSpy.close).toHaveBeenCalledWith({param1: ''});
  });
});
