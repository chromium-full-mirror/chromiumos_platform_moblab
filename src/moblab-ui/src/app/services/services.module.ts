import {NgModule} from '@angular/core';;
import {HttpModule} from '@angular/http';
import { MoblabGrpcService } from './moblab-grpc.service';

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
        { provide: MoblabGrpcService, useClass: MoblabGrpcService }
        ]
    };
  }
}

export {
  MoblabGrpcService
};
