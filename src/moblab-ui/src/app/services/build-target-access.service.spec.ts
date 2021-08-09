import { TestBed } from '@angular/core/testing';

import { BuildTargetAccessService } from './build-target-access.service';

describe('BuildTargetAccessService', () => {
  let service: BuildTargetAccessService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BuildTargetAccessService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
