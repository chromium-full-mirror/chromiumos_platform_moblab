import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { Component, Input } from '@angular/core';
import { By } from '@angular/platform-browser';
import { of } from 'rxjs/observable/of';

import { HealthChecksComponent } from './health-checks.component';
import { MobmonitorRpcService } from '../services/mobmonitor-rpc.service';
import { HealthCheck } from '../shared/health-check';
import { Action } from '../shared/action';

@Component({selector: 'mob-actions', template: ''})
class ActionsStubComponent {
  @Input()
  actions;
}

// tslint:disable-next-line
@Component({selector: 'mat-card', template: '<ng-content></ng-content>'})
class MatCardStubComponent {}

describe('HealthChecksComponent', () => {
  let component: HealthChecksComponent;
  let fixture: ComponentFixture<HealthChecksComponent>;

  const unhealthyHealthCheck: HealthCheck = {
    service: 'testService',
    health: 'unhealthy',
    errors: [{
      name: 'testCheck',
      description: 'testCheck',
      actions: ['testAction']
    }],
    warnings: []
  };
  const warningHealthCheck: HealthCheck = {
    service: 'testService',
    health: 'warning',
    errors: [],
    warnings: [{
      name: 'testCheck',
      description: 'testCheck',
      actions: []
    }]
  };
  const healthyHealthCheck: HealthCheck = {
    service: 'testService',
    health: 'healthy',
    errors: [],
    warnings: []
  };

  beforeEach(async(() => {
    const rpcSpy = jasmine.createSpyObj('MobmonitorRpcService', ['getStatus']);
    rpcSpy.getStatus.and.returnValue(of([]));
    TestBed.configureTestingModule({
      declarations: [
        HealthChecksComponent,
        ActionsStubComponent,
        MatCardStubComponent
      ],
      providers: [
        {provide: MobmonitorRpcService, useValue: rpcSpy}
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HealthChecksComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should get correct health check label', () => {
    expect(component.getHealthCheckLabel(unhealthyHealthCheck))
      .toEqual('not healthy');
    expect(component.getHealthCheckLabel(warningHealthCheck))
      .toEqual('healthy with warnings');
    expect(component.getHealthCheckLabel(healthyHealthCheck))
      .toEqual('healthy');
  });

  it('should get correct health check actions', () => {
    const expectedAction: Action = {
      action: 'testAction',
      service: 'testService',
      healthCheck: 'testCheck'
    };
    expect(component.getActionsForCheck(unhealthyHealthCheck, 'testCheck'))
      .toEqual([expectedAction]);
    expect(component.getActionsForCheck(warningHealthCheck, 'testCheck'))
      .toEqual([]);
    expect(component.getActionsForCheck(healthyHealthCheck, 'testCheck'))
      .toEqual([]);
  });

  it('should show healthy services', () => {
    const rpc = <jasmine.SpyObj<MobmonitorRpcService>> fixture.debugElement.injector.get(MobmonitorRpcService);
    // of transforms the value into an immediately emitted observable
    rpc.getStatus.and.returnValue(of([healthyHealthCheck]));

    component.ngOnInit();
    fixture.detectChanges();

    const h2 = fixture.debugElement.query(By.css('h2')).nativeElement;
    expect(h2.textContent).toContain(healthyHealthCheck.service);

    // query DOM for the status p with healthy class
    const healthStatus = fixture.debugElement.query(By.css('p.healthy')).nativeElement;
    expect(healthStatus).toBeTruthy();
    expect(healthStatus.textContent).toContain('healthy');
  });

  it('should show warning services', () => {
    const rpc = <jasmine.SpyObj<MobmonitorRpcService>> fixture.debugElement.injector.get(MobmonitorRpcService);
    rpc.getStatus.and.returnValue(of([warningHealthCheck]));

    component.ngOnInit();
    fixture.detectChanges();

    const h2 = fixture.debugElement.query(By.css('h2')).nativeElement;
    expect(h2.textContent).toContain(warningHealthCheck.service);

    const healthStatus = fixture.debugElement.query(By.css('p.warning')).nativeElement;
    expect(healthStatus).toBeTruthy();
    expect(healthStatus.textContent).toContain('healthy with warnings');
  });

  it('should show unhealthy services', () => {
    const rpc = <jasmine.SpyObj<MobmonitorRpcService>> fixture.debugElement.injector.get(MobmonitorRpcService);
    rpc.getStatus.and.returnValue(of([unhealthyHealthCheck]));

    component.ngOnInit();
    fixture.detectChanges();

    const h2 = fixture.debugElement.query(By.css('h2')).nativeElement;
    expect(h2.textContent).toContain(unhealthyHealthCheck.service);

    const healthStatus = fixture.debugElement.query(By.css('p.unhealthy')).nativeElement;
    expect(healthStatus).toBeTruthy();
    expect(healthStatus.textContent).toContain('not healthy');
  });

  it('should show multiple services', () => {
    const rpc = <jasmine.SpyObj<MobmonitorRpcService>> fixture.debugElement.injector.get(MobmonitorRpcService);
    rpc.getStatus.and.returnValue(of([
      healthyHealthCheck,
      unhealthyHealthCheck,
      warningHealthCheck
    ]));

    component.ngOnInit();
    fixture.detectChanges();

    expect(fixture.debugElement.queryAll(By.css('h2')).length).toEqual(3);
  });

  it('should update with new check data', () => {
    const rpc = <jasmine.SpyObj<MobmonitorRpcService>> fixture.debugElement.injector.get(MobmonitorRpcService);
    rpc.getStatus.and.returnValue(of([unhealthyHealthCheck], [healthyHealthCheck]));

    component.ngOnInit();
    fixture.detectChanges();

    const h2 = fixture.debugElement.query(By.css('h2')).nativeElement;
    expect(h2.textContent).toContain(healthyHealthCheck.service);

    const healthStatus = fixture.debugElement.query(By.css('p.healthy')).nativeElement;
    expect(healthStatus).toBeTruthy();
    expect(healthStatus.textContent).toContain('healthy');
  });

});
