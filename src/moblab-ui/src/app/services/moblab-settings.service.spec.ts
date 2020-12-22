import {TestBed} from '@angular/core/testing';

import {MoblabSettingsService} from './moblab-settings.service';

describe('MoblabSettingsService', () => {
  let service: MoblabSettingsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MoblabSettingsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
