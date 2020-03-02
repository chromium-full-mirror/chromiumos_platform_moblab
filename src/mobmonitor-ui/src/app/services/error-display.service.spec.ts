import { TestBed, inject } from '@angular/core/testing';
import { MatDialog } from '@angular/material/dialog';

import { ErrorDisplayService } from './error-display.service';
import { ErrorDisplayDialogComponent } from './error-display-dialog/error-display-dialog.component';
import { MobmonitorError, wrapError } from '../shared/mobmonitor-error';

describe('ErrorDisplayService', () => {
  let service: ErrorDisplayService;
  let dialogSpy: jasmine.SpyObj<MatDialog>;
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ErrorDisplayService,
        {
          provide: MatDialog,
          useValue: jasmine.createSpyObj('MatDialog', ['open'])
        }
      ]
    });
    dialogSpy = TestBed.get(MatDialog);
    service = TestBed.get(ErrorDisplayService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should open an error dialog', () => {
    const error = wrapError(
      {
        isBad: true,
        howBad: 'very'
      },
      'This is an error'
    );
    service.openErrorDialog(error);
    expect(dialogSpy.open).toHaveBeenCalledWith(ErrorDisplayDialogComponent, {
      width: '700px',
      data: error
    });
  });
});
