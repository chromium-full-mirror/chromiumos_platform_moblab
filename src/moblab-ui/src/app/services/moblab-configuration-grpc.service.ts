import {Injectable} from '@angular/core';
import * as grpcWeb from 'grpc-web';

import {MoblabConfigurationServicePromiseClient} from './moblab_configuration_rpc_grpc_web_pb';
import {Empty} from './google/protobuf/empty_pb';
import {
  PauseHostSchedulerRequest,
  PauseHostSchedulerResponse,
  ResumeHostSchedulerRequest,
  ResumeHostSchedulerResponse,
  PauseRequestor,
  GetHostSchedulerPauseStatusResponse,
} from './moblab_configuration_rpc_pb';

import {MoblabSettingsConstains} from '../constants';

@Injectable({providedIn: 'root'})
export class MoblabConfigurationGrpcService {
  configurationRpcClient = null;

  constructor() {
    const url = new URL(window.location.href);
    let service_url = new String(url.protocol);
    service_url = service_url.concat('//', url.hostname, ':', url.port, '/rpc');
    console.log(service_url);

    this.configurationRpcClient = new MoblabConfigurationServicePromiseClient(
      service_url.toString()
    );
  }

  /**
   *  Returns a promise that resolves to the list of pause requestors
   *  */
  get_pause_state() {
    return this.configurationRpcClient
      .get_host_scheduler_pause_status(new Empty())
      .then((response: GetHostSchedulerPauseStatusResponse) =>
        response.getPauserequestorsList().map(this.map_requestors)
      );
  }

  /**
   *  Request to pause host scheduling.
   *  Returns a promise that resolves to the list of pause requestors.
   *  */
  pause_host_scheduling() {
    const request = new PauseHostSchedulerRequest();
    request.setPauserequestor(PauseRequestor.PAUSE_REQUESTOR_PAUSED_BY_USER);

    return this.configurationRpcClient
      .pause_host_scheduler(request)
      .then((response: PauseHostSchedulerResponse) =>
        response.getPauserequestorsList().map(this.map_requestors)
      );
  }

  /**
   *  Request to unpause host scheduling.
   *  Returns a promise that resolves to the list of pause requestors.
   *  */
  resume_host_scheduler() {
    const request = new ResumeHostSchedulerRequest().setPauserequestor(
      PauseRequestor.PAUSE_REQUESTOR_PAUSED_BY_USER
    );

    return this.configurationRpcClient
      .resume_host_scheduler(request)
      .then((response: ResumeHostSchedulerResponse) =>
        response.getPauserequestorsList().map(this.map_requestors)
      );
  }

  private map_requestors(requestor: PauseRequestor) {
    switch (requestor) {
      case PauseRequestor.PAUSE_REQUESTOR_LOW_DISK_SPACE:
        return MoblabSettingsConstains.LOW_DISK_SPACE_STRING;
      case PauseRequestor.PAUSE_REQUESTOR_PAUSED_BY_USER:
        return MoblabSettingsConstains.USER_REQUEST_STRING;
      default:
        throw new Error('Unkown pause requestor');
    }
  }
}
