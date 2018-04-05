import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { MatSnackBar } from '@angular/material';
import { of } from 'rxjs/observable/of';
import { By } from '@angular/platform-browser';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/throw';

import { DiagnosticsComponent } from './diagnostics.component';
import { MobmonitorRpcService } from '../services/mobmonitor-rpc.service';
import { ErrorDisplayService } from '../services/error-display.service';
import { Diagnostic } from '../shared/diagnostic';

// tslint:disable-next-line
@Component({selector: 'mat-card', template: '<ng-content></ng-content>'})
class MatCardStubComponent {}

// tslint:disable-next-line
@Component({selector: 'mat-form-field', template: '<ng-content></ng-content>'})
class MatFormFieldStubComponent {}

// tslint:disable-next-line
@Component({selector: 'mat-progress-bar', template: ''})
class MatProgressBarStubComponent {}

describe('DiagnosticsComponent', () => {
  let component: DiagnosticsComponent;
  let fixture: ComponentFixture<DiagnosticsComponent>;

  const testDiagnostics: Diagnostic[] = [
    {
      category: 'test',
      checks: [{
        name: 'diagnostic check',
        description: 'a diagnostic check'
      }]
    },
    {
      category: 'another category',
      checks: [{
        name: 'another check',
        description: 'another diagnostic check'
      }]
    }
  ];

  beforeEach(async(() => {
    const rpcSpy = jasmine.createSpyObj('MobmonitorRpcService', ['listDiagnostics', 'runDiagnostic']);
    const snackSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    const errorSpy = jasmine.createSpyObj('ErrorDisplayService', ['openErrorDialog']);
    rpcSpy.listDiagnostics.and.returnValue(of([]));
    TestBed.configureTestingModule({
      declarations: [
        DiagnosticsComponent,
        MatCardStubComponent,
        MatFormFieldStubComponent,
        MatProgressBarStubComponent
      ],
      providers: [
        {provide: MobmonitorRpcService, useValue: rpcSpy},
        {provide: MatSnackBar, useValue: snackSpy},
        {provide: ErrorDisplayService, useValue: errorSpy}
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DiagnosticsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display a list of diagnostics', () => {
    const rpc = <jasmine.SpyObj<MobmonitorRpcService>> fixture.debugElement.injector.get(MobmonitorRpcService);
    rpc.listDiagnostics.and.returnValue(of(testDiagnostics));

    component.ngOnInit();
    fixture.detectChanges();

    const cards = fixture.debugElement.queryAll(By.css('.check-card'));
    expect(cards.length).toEqual(2);

    const title = cards[0].query(By.css('h2'));
    expect(title.nativeElement.textContent).toContain(testDiagnostics[0].category);

    const checkName = cards[0].query(By.css('.check-name'));
    expect(checkName.nativeElement.textContent)
      .toContain(testDiagnostics[0].checks[0].name);

    const checkDescription = cards[0].query(By.css('.check-reason'));
    expect(checkDescription.nativeElement.textContent)
      .toContain(testDiagnostics[0].checks[0].description);
  });

  it('should show error dialog on fail to list diagnostics', () => {
    const rpc = <jasmine.SpyObj<MobmonitorRpcService>> fixture.debugElement.injector.get(MobmonitorRpcService);
    rpc.listDiagnostics.and.returnValue(Observable.throw({error: 'blah'}));

    const errorDisplay = <jasmine.SpyObj<ErrorDisplayService>> fixture.debugElement.injector.get(ErrorDisplayService);
    errorDisplay.openErrorDialog.and.stub();
    component.ngOnInit();
    fixture.detectChanges();

    expect(errorDisplay.openErrorDialog).toHaveBeenCalled();
  });

  it('should run diagnostic', () => {
    const rpc = <jasmine.SpyObj<MobmonitorRpcService>> fixture.debugElement.injector.get(MobmonitorRpcService);
    const snack = <jasmine.SpyObj<MatSnackBar>> fixture.debugElement.injector.get(MatSnackBar);
    rpc.listDiagnostics.and.returnValue(of(testDiagnostics));
    rpc.runDiagnostic.and.returnValue(of({result: 'diagnostic data'}));

    component.ngOnInit();
    fixture.detectChanges();

    // click the first diagnostic button
    fixture.debugElement.query(By.css('.checks button')).nativeElement.click();

    fixture.detectChanges();

    const textarea = fixture.debugElement.query(By.css('textarea')).nativeElement;
    expect(textarea.value).toContain('diagnostic data');

    expect(snack.open).toHaveBeenCalled();
  });

  it('should show error dialog on run diagnostic fail', () => {
    const rpc = <jasmine.SpyObj<MobmonitorRpcService>> fixture.debugElement.injector.get(MobmonitorRpcService);
    const errorService = <jasmine.SpyObj<ErrorDisplayService>> fixture.debugElement.injector.get(ErrorDisplayService);
    rpc.listDiagnostics.and.returnValue(of(testDiagnostics));
    rpc.runDiagnostic.and.returnValue(Observable.throw({error: 'blah'}));

    component.ngOnInit();
    fixture.detectChanges();

    // click the first diagnostic button
    fixture.debugElement.query(By.css('.checks button')).nativeElement.click();

    fixture.detectChanges();

    expect(errorService.openErrorDialog).toHaveBeenCalled();
  });

  it('should toggle visibility of results', () => {
    const rpc = <jasmine.SpyObj<MobmonitorRpcService>> fixture.debugElement.injector.get(MobmonitorRpcService);
    rpc.listDiagnostics.and.returnValue(of(testDiagnostics));
    rpc.runDiagnostic.and.returnValue(of({result: 'diagnostic data'}));

    component.ngOnInit();
    fixture.detectChanges();

    // click the first diagnostic button
    fixture.debugElement.query(By.css('.checks button')).nativeElement.click();

    fixture.detectChanges();

    const textarea = fixture.debugElement.query(By.css('textarea')).nativeElement;

    fixture.debugElement.query(By.css('.toggle')).nativeElement.click();
    fixture.detectChanges();

    expect(textarea.hidden).toEqual(true);

    fixture.debugElement.query(By.css('.toggle')).nativeElement.click();
    fixture.detectChanges();

    expect(textarea.hidden).toEqual(false);

  });
});
