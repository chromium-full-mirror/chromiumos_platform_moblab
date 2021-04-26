import { TestBed } from '@angular/core/testing';

import { MoblabHealthCheckGuard } from './moblab-health-check.guard';

describe('MoblabHealthCheckGuard', () => {
  let guard: MoblabHealthCheckGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(MoblabHealthCheckGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
