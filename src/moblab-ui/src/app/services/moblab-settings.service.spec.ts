import {IterableDiffers} from '@angular/core';
import {TestBed} from '@angular/core/testing';

import {MoblabSettingsService} from './moblab-settings.service';
import {MoblabConfigurationGrpcService} from 'app/services/moblab-configuration-grpc.service';

class MoblabConfigurationGrpcServiceFake {
  async getPauseState() {
    return ['A'];
  }
}

describe('MoblabSettingsService', () => {
  let service: MoblabSettingsService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [{provide: MoblabConfigurationGrpcService, useClass: MoblabConfigurationGrpcServiceFake}]
    });
    service = TestBed.inject(MoblabSettingsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should update pause state when changed', () => {
    service.updateHostSchedulingStatus(['S']);
    var received = [''];
    service.pauseRequestorsObservable.subscribe(r => received = r);
    expect(received).toEqual(['S']);
  });
});
