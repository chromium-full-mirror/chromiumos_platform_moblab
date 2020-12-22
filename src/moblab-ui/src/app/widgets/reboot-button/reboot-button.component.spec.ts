import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {MatButtonModule} from '@angular/material/button';
import {
  MatDialog,
  MAT_DIALOG_DATA,
  MatDialogModule,
  MatDialogRef,
} from '@angular/material/dialog';
import {MatSnackBarModule} from '@angular/material/snack-bar';

import {ConfirmationDialog} from '../confirmation-dialog/confirmation-dialog.component';
import {RebootButtonComponent} from './reboot-button.component';

describe('RebootButtonComponent', () => {
  const mockDialogRef = {afterClosed: () => {}, close: () => {}};
  const dialogRefSpyObj = jasmine.createSpyObj(mockDialogRef);

  let buttonComponent: RebootButtonComponent;
  let buttonFixture: ComponentFixture<RebootButtonComponent>;

  let dialogSpy: jasmine.Spy;
  let rebootMoblabSpy: jasmine.Spy;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ConfirmationDialog, RebootButtonComponent],
      imports: [MatButtonModule, MatDialogModule, MatSnackBarModule],
      providers: [
        {provide: MAT_DIALOG_DATA, useValue: {}},
        {provide: MatDialogRef, useValue: mockDialogRef},
      ],
    }).compileComponents();
  }));

  function dispatchButtonClick(fixture, buttonId: string) {
    const button = fixture.debugElement.nativeElement.querySelector(buttonId);
    button.dispatchEvent(new Event('click'));
    fixture.detectChanges();
  }

  describe('button tests', () => {
    beforeEach(() => {
      buttonFixture = TestBed.createComponent(RebootButtonComponent);
      buttonComponent = buttonFixture.componentInstance;
      buttonFixture.detectChanges();

      dialogSpy = spyOn(TestBed.get(MatDialog), 'open').and.returnValue(
        dialogRefSpyObj
      );
      rebootMoblabSpy = spyOn<any>(
        // @ts-ignore
        buttonComponent.moblabGrpcService,
        'reboot_moblab'
      );
    });

    it('should compile', () => {
      expect(buttonComponent).toBeTruthy();
    });

    it('reboot click should invoke dialog.', () => {
      dispatchButtonClick(buttonFixture, '#reboot-button');
      expect(dialogSpy).toHaveBeenCalled();
    });

    it('reboot command should call-through to moblabGRPC', () => {
      buttonComponent.rebootMoblab();
      expect(rebootMoblabSpy).toHaveBeenCalled();
    });
  });
});
