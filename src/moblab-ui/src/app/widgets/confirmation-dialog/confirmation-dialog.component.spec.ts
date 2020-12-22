import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {MatButtonModule} from '@angular/material/button';
import {
  MatDialog,
  MAT_DIALOG_DATA,
  MatDialogModule,
  MatDialogRef,
} from '@angular/material/dialog';
import {MatSnackBarModule} from '@angular/material/snack-bar';

import {ConfirmationDialog} from './confirmation-dialog.component';

describe('RebootButtonComponent', () => {
  const mockDialogRef = {afterClosed: () => {}, close: () => {}};
  const dialogRefSpyObj = jasmine.createSpyObj(mockDialogRef);

  let dialogComponent: ConfirmationDialog;
  let dialogFixture: ComponentFixture<ConfirmationDialog>;

  let dialogSpy: jasmine.Spy;
  let emitSpy: jasmine.Spy;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ConfirmationDialog],
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

  describe('dialog tests', () => {
    beforeEach(() => {
      dialogFixture = TestBed.createComponent(ConfirmationDialog);
      dialogComponent = dialogFixture.componentInstance;
      dialogFixture.detectChanges();

      dialogSpy = spyOn(TestBed.get(MatDialog), 'open').and.returnValue(
        dialogRefSpyObj
      );
      emitSpy = spyOn(dialogComponent.onOk, 'emit');
    });

    it('should compile', () => {
      expect(dialogComponent).toBeTruthy();
    });

    it('should emit on ok press', () => {
      dispatchButtonClick(dialogFixture, '#ok-button');
      expect(emitSpy).toHaveBeenCalledTimes(1);
    });
  });
});
