import {NgModule} from '@angular/core';
import {MoblabRpcService} from './moblab-rpc.service';
import {HttpModule} from "@angular/http";

@NgModule({
  imports: [
    HttpModule,
  ]
})

export class ServicesModule{
  static forRoot(){
    return {
      ngModule: ServicesModule,
      providers: [MoblabRpcService]
    }
  }
}

export {
  MoblabRpcService
}
