/* tslint:disable:no-unused-variable */

import {async, inject, TestBed} from '@angular/core/testing';

import {GlobalInfoService} from './global-ui-settings.service';

describe('Service: GlobalInfo', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({providers: [GlobalInfoService]});
  });

  it('should ...', inject([GlobalInfoService], (service: GlobalInfoService) => {
    expect(service).toBeTruthy();
  }));
});
