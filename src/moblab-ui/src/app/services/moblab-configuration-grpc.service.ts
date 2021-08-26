import {Injectable} from '@angular/core';
import * as grpcWeb from 'grpc-web';

import {MoblabConfigurationServicePromiseClient} from './moblab_configuration_rpc_grpc_web_pb';
import {Empty} from './google/protobuf/empty_pb';
import {Duration} from './google/protobuf/duration_pb';
import {
  PauseHostSchedulerRequest,
  PauseHostSchedulerResponse,
  ResumeHostSchedulerRequest,
  ResumeHostSchedulerResponse,
  PauseRequestor,
  GetHostSchedulerPauseStatusResponse,
  GetStableBuildVersionRequest,
  GetStableBuildVersionResponse,
  ListStableBuildVersionsRequest,
  ListStableBuildVersionsResponse,
  SetStableBuildVersionRequest,
  SetStableBuildVersionResponse,
  GetLocalResultsRetentionDurationResponse,
  SetLocalResultsRetentionDurationRequest,
  BuildTargetStableVersion,
  StableVersion,
} from './moblab_configuration_rpc_pb';

import {MoblabSettingsConstains} from '../constants';
import {environment} from './../../environments/environment';
import {Observable, timer} from 'rxjs';
import {retryWhen, delayWhen} from 'rxjs/operators';

export class StableCrOSVersion {
  public DefaultVersion = '';
  public UserOverrideVersion = '';
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
    this.pauseStateObservable = new Observable<string[]>(observer => {
      const stream = this.configurationRpcClient.stream_host_scheduler_pause_status(
        new Empty()
      );
      stream
        .on('data', (response: GetHostSchedulerPauseStatusResponse) => {
          const pauseRequestors = response
            .getPauserequestorsList()
            .map(this.mapRequestors);
          console.log(pauseRequestors);
          observer.next(pauseRequestors);
        })
        .on('status', (status: grpcWeb.Status) => {
          console.log(
            'Status: Code: ' +
              status.code +
              'Details: ' +
              status.details +
              'Metadata: ' +
              status.metadata
          );
        })
        .on('end', () => {
          console.log('stream_host_scheduler_pause_status stream is closed!');
          observer.error('Stream ended');
        })
        .on('error', er => {
          console.log('Error in stream_host_scheduler_pause_status:', er);
          observer.error(er);
        });
    }).pipe(
      retryWhen(errors => {
        console.log('Retrying in 60s ... ');
        return errors.pipe(delayWhen(_ => timer(60000)));
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

  getStableBuildVersion(board: string): Promise<StableCrOSVersion> {
    const request = new GetStableBuildVersionRequest();
    request.setBoard(board);
    return this.configurationRpcClient
      .get_stable_build_version(request)
      .then((response: GetStableBuildVersionResponse) => {
        const result = new StableCrOSVersion();
        result.DefaultVersion = response.getStableVersion().getDefaultVersion();
        result.UserOverrideVersion = response
          .getStableVersion()
          .getOverrideVersion();
        return result;
      });
  }

  async listStableBuildVersions(): Promise<BuildTargetStableVersion[]> {
    const request = new ListStableBuildVersionsRequest();
    const response: ListStableBuildVersionsResponse = await this.configurationRpcClient.list_stable_build_versions(
      request
    );
    return response.getBuildTargetStableVersionList();
  }

  async setStableBuildVersion(
    overrideVersion: string
  ): Promise<SetStableBuildVersionResponse> {
    const request = new SetStableBuildVersionRequest();
    request.setStableVersion(
      new StableVersion().setOverrideVersion(overrideVersion)
    );
    return await this.configurationRpcClient.set_stable_build_version(request);
  }

  getResultsRetentionPeriod(): Promise<string> {
    return this.configurationRpcClient
      .get_local_results_retention_duration(new Empty())
      .then((response: GetLocalResultsRetentionDurationResponse) => {
        const hours = response.getDuration().getSeconds() / (60 * 60);
        if (hours < 24 && hours > 0) {
          return `${hours}h`;
        }
        const days = hours / 24;
        if (days < 8 && days > 0) {
          return `${days}d`;
        }
        throw new Error(`Invalid results retention duration: ${hours}`);
      });
  }

  setResultsRetentionPeriod(period: string): Promise<void> {
    let duration = Number(period.slice(0, -1));
    if (period[period.length - 1] === 'h') {
      duration = duration * 60 * 60; // Convert hours to seconds
    } else if (period[period.length - 1] === 'd') {
      duration = duration * 60 * 60 * 24; // Convert days to seconds
    } else {
      throw new Error(`Incorrect format of duration: ${period}`);
    }
    const request = new SetLocalResultsRetentionDurationRequest().setDuration(
      new Duration().setSeconds(duration)
    );
    return this.configurationRpcClient
      .set_local_results_retention_duration(request)
      .then((_: Empty) => {});
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
