import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';

import { ErrorDisplayDialogComponent } from './error-display-dialog.component';
import { MobmonitorError, wrapError } from '../../shared/mobmonitor-error';

// tslint:disable-next-line
@Component({selector: 'mat-dialog-content', template: '<ng-content></ng-content>'})
class MatDialogStubComponent {}

// tslint:disable-next-line
@Component({selector: 'mat-dialog-actions', template: '<ng-content></ng-content>'})
class MatDialogActionsStubComponent {}

describe('ErrorDisplayDialogComponent', () => {
  let component: ErrorDisplayDialogComponent;
  let fixture: ComponentFixture<ErrorDisplayDialogComponent>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<ErrorDisplayDialogComponent>>;

  const fakeError = wrapError({
      plaintains: 'too many',
      bananas: 'not enough'
    },
    'Unhandled fruit exception (not a real error, not a failed test)'
  );

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [
        ErrorDisplayDialogComponent,
        MatDialogStubComponent,
        MatDialogActionsStubComponent
      ],
      providers: [
        {
          provide: MatDialogRef,
          useValue: jasmine.createSpyObj('MatDialogRef', ['close'])
        },
        {
          provide: MAT_DIALOG_DATA,
          useValue: fakeError
        }
      ]
    })
    .compileComponents();

    dialogRefSpy = TestBed.get(MatDialogRef);
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ErrorDisplayDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have an error', () => {
    expect(component.data).toEqual(fakeError);
  });

  it('should display the error', () => {
    const title = fixture.nativeElement.querySelector('h2');
    expect(title.textContent).toContain(fakeError.message);

    const body = fixture.nativeElement.querySelector('#error-body-text');
    expect(body.value).toContain('bananas');
    expect(body.value).toContain('plaintains');

    const stacktrace = fixture.nativeElement.querySelector('#error-stacktrace');
    expect(stacktrace.value).toContain('at Object.wrapError');
  });
});
