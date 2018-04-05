import { TestBed, inject, fakeAsync, tick } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { defer } from 'rxjs/observable/defer';
import { of } from 'rxjs/observable/of';
import { ErrorObservable } from 'rxjs/observable/ErrorObservable';
import { MatDialog } from '@angular/material';

import { MobmonitorRpcService } from './mobmonitor-rpc.service';
import { HealthCheck } from '../shared/health-check';
import { Action } from '../shared/action';
import { ActionInfo } from '../shared/action-info';
import { Diagnostic } from '../shared/diagnostic';
import { DiagnosticResult } from '../shared/diagnostic-result';
import { RunDiagnosticParams } from '../shared/run-diagnostic-params';


describe('MobmonitorRpcService', () => {
  let rpc: MobmonitorRpcService;
  let httpSpy: jasmine.SpyObj<HttpClient>;
  let dialogSpy: jasmine.SpyObj<MatDialog>;

  function asyncData<T>(data: T) {
    return defer(() => Promise.resolve(data));
  }

  beforeEach(() => {

    TestBed.configureTestingModule({
      providers: [
        MobmonitorRpcService,
        {
          provide: HttpClient,
          useValue: jasmine.createSpyObj('HttpClient', ['get', 'post'])
        },
        {
          provide: MatDialog,
          useValue: jasmine.createSpyObj('MatDialog', ['open'])
        }
      ]
    });

    rpc = TestBed.get(MobmonitorRpcService);
    httpSpy = TestBed.get(HttpClient);
    dialogSpy = TestBed.get(MatDialog);
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
    const fakeAsyncRpc = new MobmonitorRpcService(httpSpy, dialogSpy);
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

    const fakeAsyncRpc = new MobmonitorRpcService(httpSpy, dialogSpy);
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

    const fakeAsyncRpc = new MobmonitorRpcService(httpSpy, dialogSpy);
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

  it('should get status not die on http error', fakeAsync(() => {
    httpSpy.get.and.returnValue(new ErrorObservable('http fail'));

    const fakeAsyncRpc = new MobmonitorRpcService(httpSpy, dialogSpy);
    let response;
    const sub = fakeAsyncRpc.getStatus().subscribe((value) => {
      response = value;
    });

    tick(1000);

    sub.unsubscribe();
    fakeAsyncRpc.ngOnDestroy();
  }));

  it('should run action', () => {
    const testAction: Action = {
      action: 'testAction',
      service: 'testService',
      healthCheck: 'testCheck'
    };

    const testActionInfo: ActionInfo = {
      action: 'testAction',
      info: 'some info about this action',
      params: {}
    };

    httpSpy.get.and.returnValue(asyncData(testActionInfo));
    httpSpy.post.and.returnValue(asyncData({}));

    rpc.runAction(testAction).subscribe(didRun => {
      expect(didRun).toEqual(true);
    });
  });

  it('should run action with params', () => {
    const testAction: Action = {
      action: 'testAction',
      service: 'testService',
      healthCheck: 'testCheck'
    };

    const testActionInfo: ActionInfo = {
      action: 'testAction',
      info: 'some info about this action',
      params: {'testparam': 'some info about param'}
    };

    httpSpy.get.and.returnValue(asyncData(testActionInfo));
    httpSpy.post.and.returnValue(asyncData({}));

    const mockDialogRef = {
      afterClosed: () => {
        return of({'testparam': 'testvalue'});
      }
    };
    dialogSpy.open.and.returnValue(mockDialogRef);

    rpc.runAction(testAction).subscribe(didRun => {
      expect(didRun).toEqual(true);
    });
  });

  it('should not run action if required params not given', () => {
    const testAction: Action = {
      action: 'testAction',
      service: 'testService',
      healthCheck: 'testCheck'
    };

    const testActionInfo: ActionInfo = {
      action: 'testAction',
      info: 'some info about this action',
      params: {'testparam': 'some info about param'}
    };

    httpSpy.get.and.returnValue(asyncData(testActionInfo));
    httpSpy.post.and.returnValue(asyncData({}));

    const mockDialogRef = {
      afterClosed: () => {
        return of(undefined);
      }
    };
    dialogSpy.open.and.returnValue(mockDialogRef);

    rpc.runAction(testAction).subscribe(didRun => {
      expect(didRun).toEqual(false);
    });
  });

  it('should error on fail get action info', () => {
    const testAction: Action = {
      action: 'testAction',
      service: 'testService',
      healthCheck: 'testCheck'
    };

    httpSpy.get.and.returnValue(new ErrorObservable({fail: true}));
    httpSpy.post.and.returnValue(of({}));

    rpc.runAction(testAction).subscribe(
      didRun => {},
      error => {
        expect(error.message).toEqual('Failed to gather action info');
        expect(error.body).toEqual({fail: true});
      }
    );
  });

  it('should list diagnostics', () => {
    const testDiagnostics: Diagnostic[] = [
      {
        category: 'test category',
        checks: [{
          name: 'test check',
          description: 'a test diagnostic'
        }]
      }
    ];
    httpSpy.get.and.returnValue(of(testDiagnostics));

    rpc.listDiagnostics().subscribe(diagnostics => {
      expect(diagnostics).toEqual(testDiagnostics);
    });
  });

  it('should error on fail list diagnostics', () => {
    httpSpy.get.and.returnValue(new ErrorObservable({fail: true}));
    rpc.listDiagnostics().subscribe(
      result => {},
      error => {
        expect(error.message).toEqual('Failed to list diagnostics');
        expect(error.body).toEqual({fail: true});
      }
    );
  });

  it('should run diagnostics', () => {
    const testParams: RunDiagnosticParams = {
      category: 'test category',
      name: 'test check name'
    };
    const testResults: DiagnosticResult = {
      result: `It's a boy.`
    };
    httpSpy.post.and.returnValue(of(testResults));

    rpc.runDiagnostic(testParams).subscribe(result => {
      expect(result).toEqual(testResults);
    });
  });

  it('should error on fail run diagnostic', () => {
    const testParams: RunDiagnosticParams = {
      category: 'test category',
      name: 'test check name'
    };
    httpSpy.post.and.returnValue(new ErrorObservable({fail: true}));

    rpc.runDiagnostic(testParams).subscribe(
      result => {},
      error => {
        expect(error.message).toEqual('Failed to run diagnostic');
        expect(error.body).toEqual({fail: true});
      }
    );
  });

});
