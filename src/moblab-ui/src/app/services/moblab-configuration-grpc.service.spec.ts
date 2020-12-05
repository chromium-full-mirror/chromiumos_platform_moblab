import {TestBed} from '@angular/core/testing';

import {MoblabGrpcService} from './moblab-grpc.service';

describe('MoblabGrpcService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: MoblabGrpcService = TestBed.get(MoblabGrpcService);
    expect(service).toBeTruthy();
  });
});
