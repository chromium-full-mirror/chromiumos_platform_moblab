import {NgModule} from '@angular/core';
import {HttpClientModule} from '@angular/common/http';

import {GlobalInfoService} from './global-ui-settings.service';
import {ConfigSetupService} from './moblab-configuration-alerting.service';
import {Feature} from './global-ui-settings.service';
import {MoblabGrpcService} from './moblab-grpc.service';

import {ModuleWithProviders} from '@angular/core';

@NgModule({
  imports: [HttpClientModule],
})
export class ServicesModule {
  static forRoot(): ModuleWithProviders<ServicesModule> {
    return {
      ngModule: ServicesModule,
      providers: [
        {provide: MoblabGrpcService, useClass: MoblabGrpcService},
        {provide: GlobalInfoService, useClass: GlobalInfoService},
        {provide: ConfigSetupService, useClass: ConfigSetupService},
      ],
    };
  }
}

export {MoblabGrpcService, GlobalInfoService, ConfigSetupService, Feature};
