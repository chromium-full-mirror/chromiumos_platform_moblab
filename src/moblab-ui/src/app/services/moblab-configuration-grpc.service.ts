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
import {environment} from './../../environments/environment';
import {Observable, timer} from 'rxjs';
import {retryWhen, delayWhen} from 'rxjs/operators';

export class StableCrOSVersion {
  public DefaultVersion: string = "";
  public UserOverrideVersion: string = "";
}

@Injectable({providedIn: 'root'})
export class MoblabConfigurationGrpcService {
  configurationRpcClient: MoblabConfigurationServicePromiseClient = null;
  pauseStateObservable: Observable<string[]>;

  constructor() {
    const url = new URL(window.location.href);
    const hostname = environment.defaultHostName || url.hostname;
    const port = environment.defaultApiPort || url.port;
    let service_url = new String(url.protocol);
    service_url = service_url.concat('//', hostname, ':', port, '/rpc');
    console.log(service_url);

    this.configurationRpcClient = new MoblabConfigurationServicePromiseClient(
      service_url.toString()
    );

    this.configurePauseStateObservable();
  }

  /**
   *  Returns a promise that resolves to the list of pause requestors
   *  */
  getPauseState() {
    return this.configurationRpcClient
      .get_host_scheduler_pause_status(new Empty())
      .then((response: GetHostSchedulerPauseStatusResponse) =>
        response.getPauserequestorsList().map(this.mapRequestors)
      );
  }

  private configurePauseStateObservable() {
    this.pauseStateObservable = new Observable<string[]>((observer) => {

      let stream = this.configurationRpcClient.stream_host_scheduler_pause_status(new Empty());
      stream
        .on('data', (response: GetHostSchedulerPauseStatusResponse) => {
          const pauseRequestors = response.getPauserequestorsList().map(this.mapRequestors)
          console.log(pauseRequestors);
          observer.next(pauseRequestors);
        })
        .on('status', (status: grpcWeb.Status) => {
          console.log(
            "Status: Code: " + status.code +
            "Details: " + status.details +
            "Metadata: " + status.metadata);
        })
        .on('end', () => {
          console.log("stream_host_scheduler_pause_status stream is closed!");
          observer.error('Stream ended');
        })
        .on('error', (er) => {
          console.log("Error in stream_host_scheduler_pause_status:", er);
          observer.error(er);
        });
    }).pipe(
      retryWhen(errors => {
        console.log("Retrying in 60s ... ");
        return errors.pipe(delayWhen(_ => timer(60000)))
      })
    );
  }

  /**
   *  Request to pause host scheduling.
   *  Returns a promise that resolves to the list of pause requestors.
   *  */
  pauseHostScheduling() {
    const request = new PauseHostSchedulerRequest();
    request.setPauserequestor(PauseRequestor.PAUSE_REQUESTOR_PAUSED_BY_USER);

    return this.configurationRpcClient
      .pause_host_scheduler(request)
      .then((response: PauseHostSchedulerResponse) =>
        response.getPauserequestorsList().map(this.mapRequestors)
      );
  }

  /**
   *  Request to unpause host scheduling.
   *  Returns a promise that resolves to the list of pause requestors.
   *  */
  resumeHostScheduler() {
    const request = new ResumeHostSchedulerRequest().setPauserequestor(
      PauseRequestor.PAUSE_REQUESTOR_PAUSED_BY_USER
    );

    return this.configurationRpcClient
      .resume_host_scheduler(request)
      .then((response: ResumeHostSchedulerResponse) =>
        response.getPauserequestorsList().map(this.mapRequestors)
      );
  }

  getStableBuildVersion() {
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

  setStableBuildVersion(override_version: string) {
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

  private mapRequestors(requestor: PauseRequestor) {
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
