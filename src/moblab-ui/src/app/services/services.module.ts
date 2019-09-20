import {NgModule} from '@angular/core';
import {HttpModule} from '@angular/http';

import {GlobalInfoService} from './global-ui-settings.service';
import {Feature} from './global-ui-settings.service';
import {MoblabGrpcService} from './moblab-grpc.service';

@NgModule({
  imports: [
    HttpModule,
  ]
})

export class ServicesModule {
  static forRoot() {
    return {
      ngModule: ServicesModule,
      providers: [
        {provide: MoblabGrpcService, useClass: MoblabGrpcService},
        {provide: GlobalInfoService, useClass: GlobalInfoService}
      ]
    };
  }
}

export {
  MoblabGrpcService,
  GlobalInfoService,
  Feature,
};
