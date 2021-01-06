import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatButtonModule} from '@angular/material/button';
import {
  MatDialog,
  MAT_DIALOG_DATA,
  MatDialogModule,
  MatDialogRef,
} from '@angular/material/dialog';
import {MatSnackBarModule} from '@angular/material/snack-bar';

import {ConfirmationDialog} from '../confirmation-dialog/confirmation-dialog.component';
import {UpdateButtonComponent} from './update-button.component';

describe('UpdateButtonComponent', () => {
  const mock_dialog_ref = {afterClosed: () => { }, close: () => { }};
  const dialogRefSpyObj = jasmine.createSpyObj(mock_dialog_ref);

  let buttonComponent: UpdateButtonComponent;
  let buttonFixture: ComponentFixture<UpdateButtonComponent>;

  let dialogSpy: jasmine.Spy;
  let isUpdateAvailableSpy: jasmine.Spy;
  let updateMoblabSpy: jasmine.Spy;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ConfirmationDialog, UpdateButtonComponent],
      imports: [
        BrowserAnimationsModule,
        MatButtonModule,
        MatDialogModule,
        MatSnackBarModule,
      ],
      providers: [
        {provide: MAT_DIALOG_DATA, useValue: {}},
        {provide: MatDialogRef, useValue: mock_dialog_ref},
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
      buttonFixture = TestBed.createComponent(UpdateButtonComponent);
      buttonComponent = buttonFixture.componentInstance;
      buttonFixture.detectChanges();

      dialogSpy = spyOn(TestBed.get(MatDialog), 'open').and.returnValue(
        dialogRefSpyObj
      );

      isUpdateAvailableSpy = spyOn<any>(
        // @ts-ignore
        buttonComponent.moblabGrpcService,
        'get_is_update_available'
      ).and.callFake(() => { });
      updateMoblabSpy = spyOn<any>(
        // @ts-ignore
        buttonComponent.moblabGrpcService,
        'update_moblab'
      );
    });

    it('should compile', () => {
      expect(buttonComponent).toBeTruthy();
    });

    it('update click should invoke dialog.', () => {
      dispatchButtonClick(buttonFixture, '.update-button');
      expect(dialogSpy).toHaveBeenCalled();
    });

    it('update command should call-through to moblabGRPC', () => {
      buttonComponent.updateMoblab();
      expect(updateMoblabSpy).toHaveBeenCalled();
    });
  });
});
