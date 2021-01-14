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
  GetStableBuildVersionRequest,
  GetStableBuildVersionResponse,
  SetStableBuildVersionRequest,
  SetStableBuildVersionResponse,
  StableVersion,
} from './moblab_configuration_rpc_pb';

import {MoblabSettingsConstains} from '../constants';

export class StableCrOSVersion {
  public DefaultVersion: string = "";
  public UserOverrideVersion: string = "";
}

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

  get_stable_build_version() {
    const request = new GetStableBuildVersionRequest();
    return this.configurationRpcClient
      .get_stable_build_version(request)
      .then((response: GetStableBuildVersionResponse) => {
        let result = new StableCrOSVersion();
        result.DefaultVersion = response.getStableVersion().getDefaultVersion();
        result.UserOverrideVersion = response.getStableVersion().getOverrideVersion();
        return result;
      });
  }

  set_stable_build_version(override_version: string) {
    const request = new SetStableBuildVersionRequest();
    request.setStableVersion(new StableVersion().setOverrideVersion(override_version));
    return this.configurationRpcClient
      .set_stable_build_version(request)
      .then((response: SetStableBuildVersionResponse) => {
        let result = new StableCrOSVersion();
        result.DefaultVersion = response.getStableVersion().getDefaultVersion();
        result.UserOverrideVersion = response.getStableVersion().getOverrideVersion();
        return result;
      });
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
