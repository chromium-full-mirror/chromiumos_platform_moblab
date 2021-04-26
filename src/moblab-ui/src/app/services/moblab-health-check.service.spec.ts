import { TestBed } from '@angular/core/testing';

import { MoblabHealthCheckService } from './moblab-health-check.service';

describe('MoblabHealthCheckService', () => {
  let service: MoblabHealthCheckService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MoblabHealthCheckService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
