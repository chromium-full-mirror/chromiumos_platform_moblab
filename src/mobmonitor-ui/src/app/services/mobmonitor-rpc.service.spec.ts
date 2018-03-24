import { TestBed, inject, fakeAsync, tick } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { defer } from 'rxjs/observable/defer';

import { MobmonitorRpcService } from './mobmonitor-rpc.service';
import { HealthCheck } from '../shared/health-check';
import { Action } from '../shared/action';
import { ActionInfo } from '../shared/action-info';


describe('MobmonitorRpcService', () => {
  let rpc: MobmonitorRpcService;
  let httpSpy: jasmine.SpyObj<HttpClient>;

  function asyncData<T>(data: T) {
    return defer(() => Promise.resolve(data));
  }

  beforeEach(() => {

    const spy = jasmine.createSpyObj('HttpClient', ['get', 'post']);

    TestBed.configureTestingModule({
      providers: [
        MobmonitorRpcService,
        {provide: HttpClient, useValue: spy}
      ]
    });

    rpc = TestBed.get(MobmonitorRpcService);
    httpSpy = TestBed.get(HttpClient);
  });

  it('should be created', () => {
    expect(rpc).toBeTruthy();
  });

  // note the fakeAsync here, used to allow us to mock
  // the passage of time for observables like interval
  it('should get status healthy', fakeAsync(() => {
    const healthyResponse = [
      {
        healthchecks: [],
        health: true,
        service: 'testService'
      }
    ];
    httpSpy.get.and.returnValue(asyncData(healthyResponse));

    // need to create an instance inside of the fakeAsync zone
    // so that the mock timing works correctly
    const fakeAsyncRpc = new MobmonitorRpcService(httpSpy);
    let response;
    const sub = fakeAsyncRpc.getStatus().subscribe((value) => {
      response = value;
    });

    // simulate 1000 ms
    tick(1000);

    const expectedValue = [{
      service: 'testService',
      health: 'healthy',
      errors: [],
      warnings: []
    }];
    expect(response).toEqual(expectedValue);

    // important to clean up subscriptions or the test will fail
    sub.unsubscribe();
    fakeAsyncRpc.ngOnDestroy();
  }));

  it('should get status warnings', fakeAsync(() => {
    const warningResponse = [
      {
        healthchecks: [
          {
            health: true,
            name: 'testCheck',
            actions: [],
            description: 'a check that produced warnings'
          }
        ],
        health: true,
        service: 'testService'
      }
    ];
    httpSpy.get.and.returnValue(asyncData(warningResponse));

    const fakeAsyncRpc = new MobmonitorRpcService(httpSpy);
    let response;
    const sub = fakeAsyncRpc.getStatus().subscribe((value) => {
      response = value;
    });

    tick(1000);

    const expectedValue = [{
      service: 'testService',
      health: 'warning',
      errors: [],
      warnings: [{
        name: 'testCheck',
        description: 'a check that produced warnings',
        actions: []
      }]
    }];
    expect(response).toEqual(expectedValue);

    sub.unsubscribe();
    fakeAsyncRpc.ngOnDestroy();
  }));

  it('should get status unhealthy', fakeAsync(() => {
    const unhealthyResponse = [
      {
        healthchecks: [
          {
            health: false,
            name: 'testCheck',
            actions: ['testAction'],
            description: 'a check that produced errors'
          }
        ],
        health: false,
        service: 'testService'
      }
    ];
    httpSpy.get.and.returnValue(asyncData(unhealthyResponse));

    const fakeAsyncRpc = new MobmonitorRpcService(httpSpy);
    let response;
    const sub = fakeAsyncRpc.getStatus().subscribe((value) => {
      response = value;
    });

    tick(1000);

    const expectedValue = [{
      service: 'testService',
      health: 'unhealthy',
      errors: [{
        name: 'testCheck',
        description: 'a check that produced errors',
        actions: ['testAction']
      }],
      warnings: []
    }];
    expect(response).toEqual(expectedValue);

    sub.unsubscribe();
    fakeAsyncRpc.ngOnDestroy();
  }));

  it('should run action', () => {
    const testAction = {
      action: 'testAction',
      service: 'testService',
      healthCheck: 'testCheck'
    };

    const testActionInfo = {
      action: 'testAction',
      info: 'some info about this action',
      args: [],
      kwargs: {}
    };

    httpSpy.get.and.returnValue(asyncData(testActionInfo));
    httpSpy.post.and.returnValue(asyncData({}));

    rpc.runAction(testAction);
  });


});
