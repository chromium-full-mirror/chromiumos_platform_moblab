import {NgModule} from '@angular/core';
import {MoblabRpcService} from './moblab-rpc.service';
import {HttpModule} from "@angular/http";
import {MoblabRpcServiceMock} from "./moblab-rpc-service-mock";

@NgModule({
  imports: [
    HttpModule,
  ]
})

export class ServicesModule{
  static forRoot(){
    return {
      ngModule: ServicesModule,
      providers: [
        { provide: MoblabRpcService, useClass: MoblabRpcServiceMock }
        ]
    }
  }
}

export {
  MoblabRpcService
}
