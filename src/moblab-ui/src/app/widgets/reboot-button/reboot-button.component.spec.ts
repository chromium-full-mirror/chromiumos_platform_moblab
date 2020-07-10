import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {MatButtonModule} from '@angular/material/button';
import {
  MatDialog,
  MAT_DIALOG_DATA,
  MatDialogModule,
  MatDialogRef
} from '@angular/material/dialog';
import {MatSnackBarModule} from '@angular/material/snack-bar';

import {ConfirmationDialog, RebootButtonComponent} from './reboot-button';


describe('RebootButtonComponent', () => {
  const mock_dialog_ref = { afterClosed : () => {}, close: () => {} }
  const dialogRefSpyObj = jasmine.createSpyObj(mock_dialog_ref);

  let buttonComponent: RebootButtonComponent;
  let dialogComponent: ConfirmationDialog;
  let buttonFixture: ComponentFixture<RebootButtonComponent>;
  let dialogFixture: ComponentFixture<ConfirmationDialog>;

  let dialogSpy: jasmine.Spy;
  let rebootMoblabSpy: jasmine.Spy;

  beforeEach(async(() => {
    TestBed
      .configureTestingModule({
        declarations: [
          ConfirmationDialog,
          RebootButtonComponent,
        ],
        imports: [
          MatButtonModule,
          MatDialogModule,
          MatSnackBarModule
        ],
        providers: [
          { provide: MAT_DIALOG_DATA, useValue: {} },
          { provide: MatDialogRef, useValue: mock_dialog_ref }
        ],
      })
      .compileComponents();
  }));

  function dispatchButtonClick(fixture, buttonId: string) {
    const button = fixture.debugElement.nativeElement.querySelector(
      buttonId
    );
    button.dispatchEvent(new Event('click'));
    fixture.detectChanges();
  }

  describe('button tests', function () {
    beforeEach(() => {
      buttonFixture = TestBed.createComponent(RebootButtonComponent);
      buttonComponent = buttonFixture.componentInstance;
      buttonFixture.detectChanges();

      dialogSpy = spyOn(TestBed.get(MatDialog), 'open')
        .and.returnValue(dialogRefSpyObj);
    });

    it('should compile', () => {
      expect( buttonComponent).toBeTruthy();
    });

    it('reboot click should invoke dialog.', () => {
      dispatchButtonClick(buttonFixture, '#reboot-button');
      expect(dialogSpy).toHaveBeenCalled();
    });
  });

  describe('dialog tests', function () {
    beforeEach(() => {
      dialogFixture = TestBed.createComponent(ConfirmationDialog);
      dialogComponent = dialogFixture.componentInstance;
      dialogFixture.detectChanges();

      dialogSpy = spyOn(TestBed.get(MatDialog), 'open')
        .and.returnValue(dialogRefSpyObj);
      // @ts-ignore
      rebootMoblabSpy = spyOn<any>(
        dialogComponent.moblabGrpcService,
        'reboot_moblab'
      );
    });

    it('should compile', () => {
      expect(dialogComponent).toBeTruthy();
    });

    it('should invoke reboot', () => {
      dispatchButtonClick(dialogFixture,'#reboot-ok-button');
      expect(rebootMoblabSpy).toHaveBeenCalled();
    });
  });
});
