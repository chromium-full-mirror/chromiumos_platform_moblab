import {TestBed} from '@angular/core/testing';

import {MoblabRebootCheckService} from './moblab-reboot-check.service';

describe('MoblabRebootCheckService', () => {
  let service: MoblabRebootCheckService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MoblabRebootCheckService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
