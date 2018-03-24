import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { MatSnackBar } from '@angular/material';
import { of } from 'rxjs/observable/of';

import { MobmonitorRpcService } from '../services/mobmonitor-rpc.service';
import { ActionsComponent } from './actions.component';


describe('ActionsComponent', () => {
  let component: ActionsComponent;
  let fixture: ComponentFixture<ActionsComponent>;

  beforeEach(async(() => {
    const rpcSpy = jasmine.createSpyObj('MobmonitorRpcService', ['runAction']);
    const snackSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    TestBed.configureTestingModule({
      declarations: [
        ActionsComponent
      ],
      providers: [
        {provide: MobmonitorRpcService, useValue: rpcSpy},
        {provide: MatSnackBar, useValue: snackSpy}
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ActionsComponent);
    component = fixture.componentInstance;
    component.actions = [{
      action: 'testAction',
      service: 'testService',
      healthCheck: 'testCheck'
    }];
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have buttons for the actions', () => {
    const button = fixture.debugElement.query(By.css('button')).nativeElement;
    expect(button.textContent).toContain('testAction');
  });

  it('should run action when clicked', () => {
    const rpc = <jasmine.SpyObj<MobmonitorRpcService>> fixture.debugElement.injector.get(MobmonitorRpcService);
    const snackBar = <jasmine.SpyObj<MatSnackBar>> fixture.debugElement.injector.get(MatSnackBar);

    rpc.runAction.and.returnValue(of({}));

    const button = fixture.debugElement.query(By.css('button'));
    button.triggerEventHandler('click', null);

    expect(rpc.runAction.calls.count()).toBe(1);
    expect(snackBar.open.calls.count()).toBe(1);
  });
});
