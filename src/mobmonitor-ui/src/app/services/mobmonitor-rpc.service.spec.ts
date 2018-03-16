import { TestBed, inject } from '@angular/core/testing';

import { MobmonitorRpcService } from './mobmonitor-rpc.service';

describe('MobmonitorRpcService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [MobmonitorRpcService]
    });
  });

  it('should be created', inject([MobmonitorRpcService], (service: MobmonitorRpcService) => {
    expect(service).toBeTruthy();
  }));
});
