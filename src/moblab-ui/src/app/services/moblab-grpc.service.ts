import {Injectable} from '@angular/core';
import {Empty} from 'google-protobuf/google/protobuf/empty_pb';
import * as grpcWeb from 'grpc-web';

import {
  MoblabRpcServiceClient,
  MoblabRpcServicePromiseClient,
} from './moblabrpc_grpc_web_pb';
import {ConfigSetupService} from './moblab-configuration-alerting.service';
import {environment} from '../../environments/environment';
import {BUILD_STATUS_MAPPINGS} from '../utils/proto_helpers';
import {
  AbortJobsRequest,
  AbortJobsResponse,
  AddAttributeToDutsRequest,
  AddAttributeToDutsResponse,
  AddLabelToDutsRequest,
  AddLabelToDutsResponse,
  AddPoolToDutsRequest,
  AddPoolToDutsResponse,
  AddServoRequest,
  AddServoResponse,
  ConnectedDutFirmwareInfo,
  ConnectedDutInfo,
  DutTask,
  EnrollDutsRequest,
  EnrollDutsResponse,
  GetCloudConfigurationRequest,
  GetCloudConfigurationResponse,
  GetDutWifiInfoRequest,
  GetDutWifiInfoResponse,
  GetDutDetailsRequest,
  GetDutDetailsResponse,
  GetDutTasksRequest,
  GetDutTasksResponse,
  GetIsUpdateAvailableRequest,
  GetIsUpdateAvailableResponse,
  GetJobDetailsRequest,
  GetJobDetailsResponse,
  GetJobIdsResponse,
  GetJobsRequest,
  GetJobsResponse,
  GetNetworkInfoRequest,
  GetNetworkInfoResponse,
  GetNumDutTasksRequest,
  GetNumDutTasksResponse,
  GetNumJobsRequest,
  GetNumJobsResponse,
  GetRemoteAgentConfigurationRequest,
  GetRemoteAgentConfigurationResponse,
  GetSystemInfoRequest,
  GetSystemInfoResponse,
  GetVersionInfoRequest,
  GetVersionInfoResponse,
  Job,
  ListBuildTargetsRequest,
  ListBuildTargetsByModelRequest,
  ListBuildTargetsByModelResponse,
  ListBuildVersionsRequest,
  ListBuildVersionsResponse,
  ListConnectedDutsFirmwareResponse,
  ListConnectedDutsRequest,
  ListConnectedDutsResponse,
  ListMilestonesRequest,
  ListMilestonesResponse,
  ListModelsRequest,
  ListModelsResponse,
  ListAccessibleModelsRequest,
  ListPoolsRequest,
  ListPoolsResponse,
  Model,
  RebootMoblabRequest,
  RebootMoblabResponse,
  RemoveAttributeFromDutsRequest,
  RemoveAttributeFromDutsResponse,
  RemoveLabelFromDutsRequest,
  RemoveLabelFromDutsResponse,
  RemovePoolFromDutsRequest,
  RemovePoolFromDutsResponse,
  RepairHostRequest,
  RepairHostResponse,
  ReverifyHostRequest,
  ReverifyHostResponse,
  RunCtsSuiteRequest,
  RunGtsSuiteRequest,
  RunMemoryQualificationSuiteRequest,
  RunStorageQualificationSuiteRequest,
  RunFAFTSuiteRequest,
  RunSuiteRequest,
  RunSuiteResponse,
  SendMoblabScreenshotRequest,
  SendMoblabScreenshotResponse,
  SetCloudConfigurationRequest,
  SetCloudConfigurationResponse,
  SetDutWifiInfoRequest,
  SetDutWifiInfoResponse,
  SetRemoteAgentConfigurationRequest,
  SetRemoteAgentConfigurationResponse,
  UpdateDutsFirmwareRequest,
  UpdateDutsFirmwareResponse,
  UpdateMoblabRequest,
  UpdateMoblabResponse,
  FirmwareUpdateCommandOutput,
  ValidateStorageQualSetupRequest,
  ProvisionDutsRequest,
  StageBuildRequest,
  StageBuildResponse,
  BuildItem,
  GetPeripheralInformationRequest,
  GetPeripheralInformationResponse,
  RunFWUPDSuiteRequest,
} from './moblabrpc_pb';

@Injectable({providedIn: 'root'})
export class MoblabGrpcService {
  moblabRpcService: MoblabRpcServiceClient = null;
  moblabRpcServicePromiseClient: MoblabRpcServicePromiseClient = null;
  public service_address: String;

  constructor(private configSetupService: ConfigSetupService) {
    const url = new URL(window.location.href);
    const hostname = environment.defaultHostName || url.hostname;
    const port = environment.defaultApiPort || url.port;
    let service_url = new String(url.protocol);

    service_url = service_url.concat('//', hostname, ':', port);
    this.service_address = service_url;

    service_url = service_url.concat('/rpc');
    console.log(service_url);

    this.moblabRpcService = new MoblabRpcServiceClient(service_url.toString());
    this.moblabRpcServicePromiseClient = new MoblabRpcServicePromiseClient(
      service_url.toString()
    );
  }

  /** Method for submitting feedback and screenshots to Moblab-associated GCS
   *  bucket.
   *  @param callback: function invoked in success scenarios.
   *  @param error_callback: function invoked in failure scenarios.
   *  @param description: User-submitted text describing motivation of feedback
   *    submission.
   *  @param screenshot: Serialized, Base64 png screenshot image.
   * */
  sendMoblabScreenshot(
    callback: (message: string) => void,
    error_callback: (message: string) => void,
    contact_email: string,
    description: string,
    screenshot: string
  ) {
    const request = new SendMoblabScreenshotRequest();
    request.setContactEmail(contact_email);
    request.setDescription(description);

    if (screenshot) {
      // screenshot is optional in the feedback modal
      request.setScreenshot(screenshot.substring(screenshot.indexOf(',') + 1));
    }

    this.moblabRpcService.send_moblab_screenshot(
      request,
      {},
      (err: grpcWeb.Error, response: SendMoblabScreenshotResponse) => {
        if (err) {
          error_callback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  /** Generic run suite method that can run any of the specific suites defined below
   *  ( with no suite-specific options ).
   *  @param callback: function invoked in success scenarios.
   *  @param error_callback: function invoked in failure scenarios.
   *  @param suite_name: ex. CTS, GTS.
   *  @param build: String name of build the suite is being run under.
   *  @param buildtarget: ex. XXX-release/R99-99999.9.9
   *  @param model: Device model.
   *  @param pool: String identifer of a group of DUTs
   *    (as configured in the 'Manage DUTs' component )
   * */
  runSuite(
    callback: (response: RunSuiteResponse) => void,
    error_callback: (err: grpcWeb.Error, response: RunSuiteResponse) => void,
    suite_name: string,
    build: string,
    milestone: string,
    buildtarget: string,
    model: string,
    pool: string
  ) {
    const request = new RunSuiteRequest();
    request.setSuite(suite_name);
    request.setBuildVersion(build);
    request.setMilestone(milestone);
    request.setBuildTarget(buildtarget);
    request.setModel(model);
    request.setPool(pool);

    this.moblabRpcService.run_suite(
      request,
      {},
      (err: grpcWeb.Error, response: RunSuiteResponse) => {
        if (err) {
          error_callback(err, response);
        } else {
          callback(response);
        }
      }
    );
  }

  /** Starts CTS suite run.
   *  @param callback: function invoked in success scenarios.
   *  @param error_callback: function invoked in failure scenarios.
   *  @param android_version: ex. String identifier indicating the android
   *    version the CTS suite is being run for (ex. CTS_N ).
   *  @param build: String name of build the suite is being run under.
   *  @param buildtarget: ex. XXX-release/R99-99999.9.9
   *  @param model: Device model.
   *  @param pool: String identifer of a group of DUTs
   *    (as configured in the 'Manage DUTs' component ).
   *  @param specific_modules_list: Comma separated string containing names of
   *    CTS modules. If not empty, only modules in this list will be run as a
   *    part of suite execution.
   * */
  runCtsSuite(
    callback: (response: RunSuiteResponse) => void,
    error_callback: (err: grpcWeb.Error, response: RunSuiteResponse) => void,
    android_version: string,
    build: string,
    milestone: string,
    buildtarget: string,
    model: string,
    pool: string,
    specific_modules_list: string[]
  ) {
    const request = new RunCtsSuiteRequest();
    request.setAndroidVersion(android_version);
    request.setBuildVersion(build);
    request.setBuildTarget(buildtarget);
    request.setMilestone(milestone);
    request.setModel(model);
    request.setPool(pool);
    request.setSpecificModulesList(specific_modules_list);

    this.moblabRpcService.run_cts_suite(
      request,
      {},
      (err: grpcWeb.Error, response: RunSuiteResponse) => {
        if (err) {
          error_callback(err, response);
        } else {
          callback(response);
        }
      }
    );
  }

  /** Starts GTS suite run.
   *  @param callback: function invoked in success scenarios.
   *  @param error_callback: function invoked in failure scenarios.
   *  @param build: String name of build the suite is being run under.
   *  @param buildtarget: ex. XXX-release/R99-99999.9.9
   *  @param model: Device model.
   *  @param pool: String identifer of a group of DUTs
   *    (as configured in the 'Manage DUTs' component ).
   *  @param specific_modules_list: Comma separated string containing names ofss
   *    GTS modules. If not empty, only modules in this list will be run as a
   *    part of suite execution.
   * */
  runGtsSuite(
    callback: (response: RunSuiteResponse) => void,
    error_callback: (err: grpcWeb.Error, response: RunSuiteResponse) => void,
    build: string,
    milestone: string,
    buildtarget: string,
    model: string,
    pool: string,
    specific_modules_list: string[]
  ) {
    const request = new RunGtsSuiteRequest();
    request.setBuildVersion(build);
    request.setBuildTarget(buildtarget);
    request.setModel(model);
    request.setMilestone(milestone);
    request.setPool(pool);
    request.setSpecificModulesList(specific_modules_list);

    this.moblabRpcService.run_gts_suite(
      request,
      {},
      (err: grpcWeb.Error, response: RunSuiteResponse) => {
        if (err) {
          error_callback(err, response);
        } else {
          callback(response);
        }
      }
    );
  }

  /** Starts hardware storage qualification suite run.
   *  @param callback: function invoked in success scenarios.
   *  @param error_callback: function invoked in failure scenarios.
   *  @param build: String name of build the suite is being run under.
   *  @param buildtarget: ex. XXX-release/R99-99999.9.9
   *  @param model: Device model.
   *  @param pool: String identifer of a group of DUTs
   *    (as configured in the 'Manage DUTs' component ).
   *  @param avl_process_bug_id: ID of buganizer issue associated with this
   *    storage qualification run.
   *  @param avl_part_number: Number identifier of part for which qualification
   *    is being run.
   *  @param variation: Number enum that identifies a variation of storage qual
   *    to run.
   *  */
  runStorageQualificationSuite(
    callback: (response: RunSuiteResponse) => void,
    error_callback: (err: grpcWeb.Error, response: RunSuiteResponse) => void,
    build: string,
    milestone: string,
    buildtarget: string,
    model: string,
    pool: string,
    avl_process_bug_id: string,
    avl_part_number: string,
    variation: number,
    disk_size_gb: number,
    dual_namespace: boolean,
    is_pre_qualified: boolean
  ) {
    const request = new RunStorageQualificationSuiteRequest();
    request.setBuildVersion(build);
    request.setMilestone(milestone);
    request.setBuildTarget(buildtarget);
    request.setModel(model);
    request.setPool(pool);
    request.setAvlProcessBugId(avl_process_bug_id);
    request.setAvlPartNumber(avl_part_number);
    request.setVariation(variation);
    request.setDiskSizeGb(disk_size_gb);
    request.setIsDualNamespace(dual_namespace);
    request.setIsPreQualified(is_pre_qualified);

    this.moblabRpcService.run_storage_qualification_suite(
      request,
      {},
      (err: grpcWeb.Error, response: RunSuiteResponse) => {
        if (err) {
          error_callback(err, response);
        } else {
          callback(response);
        }
      }
    );
  }

  /** Starts hardware memory qualification suite run.
   *  @param callback: function invoked in success scenarios.
   *  @param error_callback: function invoked in failure scenarios.
   *  @param build: String name of build the suite is being run under.
   *  @param buildtarget: ex. XXX-release/R99-99999.9.9
   *  @param model: Device model.
   *  @param pool: String identifer of a group of DUTs
   *    (as configured in the 'Manage DUTs' component ).
   *  @param avl_process_bug_id: ID of buganizer issue associated with this
   *    qualification run.
   *  @param avl_part_number: Number identifier of part for which qualification
   *    is being run.
   *  */
  runMemoryQualificationSuite(
    callback: (response: RunSuiteResponse) => void,
    error_callback: (err: grpcWeb.Error, response: RunSuiteResponse) => void,
    build: string,
    milestone: string,
    buildtarget: string,
    model: string,
    pool: string,
    avl_process_bug_id: string,
    avl_part_number: string
  ) {
    const request = new RunMemoryQualificationSuiteRequest();
    request.setBuildVersion(build);
    request.setMilestone(milestone);
    request.setBuildTarget(buildtarget);
    request.setModel(model);
    request.setPool(pool);
    request.setAvlProcessBugId(avl_process_bug_id);
    request.setAvlPartNumber(avl_part_number);

    this.moblabRpcService.run_memory_qualification_suite(
      request,
      {},
      (err: grpcWeb.Error, response: RunSuiteResponse) => {
        if (err) {
          error_callback(err, response);
        } else {
          callback(response);
        }
      }
    );
  }

  /** Starts FAFT suite run.
   *  @param callback: function invoked in success scenarios.
   *  @param error_callback: function invoked in failure scenarios.
   *  @param suite: ex. String identifier indicating the faft suite to run.
   *  @param build: String name of build the suite is being run under.
   *  @param buildtarget: ex. XXX-release/R99-99999.9.9
   *  @param model: Device model.
   *  @param pool: String identifer of a group of DUTs
   *    (as configured in the 'Manage DUTs' component ).
   *  @param specific_test_list: Comma separated string containing names of
   *    tests in the suite. If not empty, only tests in this list will be
   *    run as a part of suite execution.
   * */
  runFAFTSuite(
    callback: (response: RunSuiteResponse) => void,
    error_callback: (err: grpcWeb.Error, response: RunSuiteResponse) => void,
    suite: string,
    build: string,
    milestone: string,
    buildtarget: string,
    model: string,
    pool: string,
    specific_test_list: string[]
  ) {
    const request = new RunFAFTSuiteRequest();
    request.setSuite(suite);
    request.setBuildVersion(build);
    request.setBuildTarget(buildtarget);
    request.setMilestone(milestone);
    request.setModel(model);
    request.setPool(pool);
    request.setSpecificTestsList(specific_test_list);

    this.moblabRpcService.run_faft_suite(
      request,
      {},
      (err: grpcWeb.Error, response: RunSuiteResponse) => {
        if (err) {
          error_callback(err, response);
        } else {
          callback(response);
        }
      }
    );
  }

   /** Starts FWUPD suite run.
   *  @param callback: function invoked in success scenarios.
   *  @param error_callback: function invoked in failure scenarios.
   *  @param suite: ex. String identifier indicating the faft suite to run.
   *  @param build: String name of build the suite is being run under.
   *  @param buildtarget: ex. XXX-release/R99-99999.9.9
   *  @param model: Device model.
   *  @param pool: String identifer of a group of DUTs
   *    (as configured in the 'Manage DUTs' component ).
   *  @param test_args: set of test args passed to test/suite during the 
   *    test execution.
   * */
     runFWUPDSuite(
      callback: (response: RunSuiteResponse) => void,
      error_callback: (err: grpcWeb.Error, response: RunSuiteResponse) => void,
      suite: string,
      build: string,
      milestone: string,
      buildtarget: string,
      model: string,
      pool: string,
      test_args: string[]
    ) {
      const request = new RunFWUPDSuiteRequest();
      request.setSuite(suite);
      request.setBuildVersion(build);
      request.setBuildTarget(buildtarget);
      request.setMilestone(milestone);
      request.setModel(model);
      request.setPool(pool);
      request.setTestArgsList(test_args);
  
      this.moblabRpcService.run_fwupd_suite(
        request,
        {},
        (err: grpcWeb.Error, response: RunSuiteResponse) => {
          if (err) {
            error_callback(err, response);
          } else {
            callback(response);
          }
        }
      );
    }

  /** Starts provision suite run.
   *  @param callback: function invoked in success scenarios.
   *  @param error_callback: function invoked in failure scenarios.
   *  @param build: String name of build the suite is being run under.
   *  @param milestone: String identifer of a milestone.
   *  @param model: Device model.
   *  @param pool: String identifer of a group of DUTs
   *    (as configured in the 'Manage DUTs' component )
   * */
  provisionDuts(
    callback: () => void,
    error_callback: (err: string) => void,
    build: string,
    milestone: string,
    pool: string
  ) {
    const request = new ProvisionDutsRequest();
    request.setBuildVersion(build);
    request.setMilestone(milestone);
    request.setPool(pool);

    this.moblabRpcService.provision_duts(
      request,
      {},
      (err: grpcWeb.Error, _: Empty) => {
        if (err) {
          error_callback(err.message);
        } else {
          callback();
        }
      }
    );
  }

  async stageBuildPromise(
    model: string,
    build_target: string,
    build_version: string
  ): Promise<string> {
    /** Stage the given build on the bucket configured on this moblab.
     * */
    const request = new StageBuildRequest();
    request.setModel(model);
    request.setBuildTarget(build_target);
    request.setBuildVersion(build_version);
    const response = await this.moblabRpcServicePromiseClient.stage_build(
      request
    );
    return response.getBuildBucket();
  }

  listConnectedDuts(
    callback: (x: ConnectedDutInfo[]) => void,
    error_callback: (err: string) => void
  ) {
    const request = new ListConnectedDutsRequest();

    this.moblabRpcService.list_connected_duts(
      request,
      {},
      (err: grpcWeb.Error, response: ListConnectedDutsResponse) => {
        if (err) {
          console.log(err);
          error_callback('Failed to fetch DUTs');
        } else {
          callback(response.getDutsList());
        }
      }
    );
  }

  getDutDetails(
    callback: (x: ConnectedDutInfo) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut: string
  ) {
    const request = new GetDutDetailsRequest();
    request.setDut(dut);

    this.moblabRpcService.get_dut_details(
      request,
      {},
      (err: grpcWeb.Error, response: GetDutDetailsResponse) => {
        if (err) {
          console.log(
            'Failed get_dut_details RPC call. Request: ',
            request,
            'Response: ',
            err
          );
          errorHandlingCallback(err.message);
        } else {
          callback(response.getDutDetail());
        }
      }
    );
  }

  getNumJobs(
    callback: (x: number) => void,
    // TODO(b/189210905): It can be a bit awkward to call this method when only
    // 1 or 2 arguments need to be passed. Utilize JS object destructuring to
    // make calling this method more readable.
    id_filter?: string,
    name_filter?: string,
    created_time_lt?: number,
    created_time_gt?: number,
    status_filter?: Job.QueueStatus,
    rel_filter?: Job.Relationship,
    parent_id_filter?: string,
    dut_hostname_filter?: string
  ) {
    const request = new GetNumJobsRequest();
    if (id_filter) {
      request.setIdFilter(id_filter);
    }
    if (name_filter) {
      request.setNameFilter(name_filter);
    }
    if (created_time_lt) {
      request.setCreatedTimeLt(created_time_lt);
    }
    if (created_time_gt) {
      request.setCreatedTimeGt(created_time_gt);
    }
    if (status_filter) {
      request.setStatusFilter(status_filter);
    }
    if (rel_filter) {
      request.setRelFilter(rel_filter);
    }
    if (parent_id_filter) {
      request.setParentIdFilter(parent_id_filter);
    }
    if (dut_hostname_filter) {
      request.setDutHostnameFilter(dut_hostname_filter);
    }

    this.moblabRpcService.get_num_jobs(
      request,
      {},
      (err: grpcWeb.Error, response: GetNumJobsResponse) => {
        if (err) {
          console.log(
            'Failed get_num_jobs RPC call. Request: ',
            request,
            'Response: ',
            err
          );
        } else {
          callback(response.getNumJobs());
        }
      }
    );
  }

  getJobs(
    callback: (x: Job[]) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    queryStart: number,
    queryLimit: number,
    id_filter?: string,
    name_filter?: string,
    created_time_lt?: number,
    created_time_gt?: number,
    status_filter?: Job.QueueStatus,
    rel_filter?: Job.Relationship,
    parent_id_filter?: string,
    dut_hostname_filter?: string,
    sort_by?: string
  ) {
    const request = new GetJobsRequest();
    request.setQueryStart(queryStart);
    request.setQueryLimit(queryLimit);
    if (id_filter) {
      request.setIdFilter(id_filter);
    }
    if (name_filter) {
      request.setNameFilter(name_filter);
    }
    if (created_time_lt) {
      request.setCreatedTimeLt(created_time_lt);
    }
    if (created_time_gt) {
      request.setCreatedTimeGt(created_time_gt);
    }
    if (status_filter) {
      request.setStatusFilter(status_filter);
    }
    if (rel_filter) {
      request.setRelFilter(rel_filter);
    }
    if (parent_id_filter) {
      request.setParentIdFilter(parent_id_filter);
    }
    if (dut_hostname_filter) {
      request.setDutHostnameFilter(dut_hostname_filter);
    }
    if (sort_by) {
      request.setSortBy(sort_by);
    }

    this.moblabRpcService.get_jobs(
      request,
      {},
      (err: grpcWeb.Error, response: GetJobsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
          console.log(
            'Failed get_jobs RPC call. Request: ',
            request,
            'Response: ',
            err
          );
        } else {
          callback(response.getJobsList());
        }
      }
    );
  }

  getJobIds(
    callback: (job_ids: number[]) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    queryStart: number,
    queryLimit: number,
    id_filter?: string,
    name_filter?: string,
    created_time_lt?: number,
    created_time_gt?: number,
    status_filter?: Job.QueueStatus,
    rel_filter?: Job.Relationship,
    parent_id_filter?: string,
    dut_hostname_filter?: string
  ) {
    /**
     *  Calls moblab RPC for a list of job IDs matching given query parameters.
     *  @param callback: Invoked on successful return of job IDs.
     *  @param errorCallback: Invoked on call failures.
     *  @param queryStart: Number representing index for start of returned values.
     *  @param queryLimit: Number representing max number of values to return.
     *  @param id_filter: String filter for job id.
     *  @param name_filter: String filter for job name.
     *  @param created_time_lt: A unix timestamp in seconds granularity the sets
     *         upper bound for jobs returned.
     *  @param created_time_gt: A unix timestamp in seconds granularity the sets
     *         lower bound for jobs returned.
     *  @param status_filter: Job.QueueStatus filter for returned jobs.
     *  @param rel_filter: Job.Relationship (child vs parent) for returned jobs.
     *  @param parent_id_filter: String that filters jobs by parent job id.
     *  @param dut_hostname_filter: String that filters jobs by associated
     *         DUT.
     */
    const request = new GetJobsRequest();
    request.setQueryStart(queryStart);
    request.setQueryLimit(queryLimit);
    if (id_filter) {
      request.setIdFilter(id_filter);
    }
    if (name_filter) {
      request.setNameFilter(name_filter);
    }
    if (created_time_lt) {
      request.setCreatedTimeLt(created_time_lt);
    }
    if (created_time_gt) {
      request.setCreatedTimeGt(created_time_gt);
    }
    if (status_filter) {
      request.setStatusFilter(status_filter);
    }
    if (rel_filter) {
      request.setRelFilter(rel_filter);
    }
    if (parent_id_filter) {
      request.setParentIdFilter(parent_id_filter);
    }
    if (dut_hostname_filter) {
      request.setDutHostnameFilter(dut_hostname_filter);
    }

    this.moblabRpcService.get_job_ids(
      request,
      {},
      (err: grpcWeb.Error, response: GetJobIdsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getJobIdsList());
        }
      }
    );
  }

  abortJobs(
    callback: (resultMsg: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    jobIds: number[]
  ) {
    const request = new AbortJobsRequest();
    request.setJobIdsList(jobIds);

    this.moblabRpcService.abort_jobs(
      request,
      {},
      (err: grpcWeb.Error, response: AbortJobsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  getJobDetails(
    callback: (x: Job) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    id: string
  ) {
    const request = new GetJobDetailsRequest();
    request.setId(id);

    this.moblabRpcService.get_job_details(
      request,
      {},
      (err: grpcWeb.Error, response: GetJobDetailsResponse) => {
        if (err) {
          console.log(
            'Failed get_job_details RPC call. Request: ',
            request,
            'Response: ',
            err
          );
          errorHandlingCallback(err.message);
        } else {
          callback(response.getJobDetail());
        }
      }
    );
  }

  listBuildTargetsByModel(
    model: string,
    callback: (x: string[]) => void,
    errorHandlingCallback: (err_msg: string) => void
  ) {
    /** Returns the build_target(s) associated with the given model.
     *  @param model: target model
     *  @param callback: function invoked in success scenarios.
     *  @param error_callback: function invoked in failure scenarios.
     * */
    const request = new ListBuildTargetsByModelRequest();
    request.setModel(model);

    this.moblabRpcService.list_build_targets_by_model(
      request,
      {},
      (err: grpcWeb.Error, response: ListBuildTargetsByModelResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getBuildTargetsList());
        }
      }
    );
  }

  async listBuildTargetsPromise(): Promise<string[]> {
    /** Returns the build_target(s) that the account has access to as promise.
     * */
    const request = new ListBuildTargetsRequest();
    const response = await this.moblabRpcServicePromiseClient.list_build_targets(
      request
    );
    return response.getBuildTargetsList();
  }

  listMilestones(
    buildtarget: string,
    model: string,
    callback: (milestones: string[], isIncomplete: boolean) => void,
    errorHandlingCallback: (err_msg: string) => void
  ) {
    const request = new ListMilestonesRequest();
    request.setBuildTarget(buildtarget);
    request.setModel(model);

    this.moblabRpcService.list_milestones(
      request,
      {},
      (err: grpcWeb.Error, response: ListMilestonesResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          const milestoneNames = [];
          for (const item of response.getMilestonesList()) {
            milestoneNames.push(item.getValue());
          }
          callback(milestoneNames, response.getIsIncomplete());
        }
      }
    );
  }

  listBuildVersions(
    buildtarget: string,
    model: string,
    milestone: string,
    label: string,
    labelName: string,
    callback: (
      buildVersions: {version: string; status: string}[],
      isIncomplete: boolean
    ) => void,
    errorHandlingCallback: (err_msg: string) => void
  ) {
    const request = new ListBuildVersionsRequest();
    request.setBuildTarget(buildtarget);
    request.setModel(model);
    request.setMilestone(milestone);
    request.setLabel(label);
    this.moblabRpcService.list_build_versions(
      request,
      {},
      (err: grpcWeb.Error, response: ListBuildVersionsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          const buildVersionNames = [];
          for (const item of response.getBuildVersionsList()) {
            let buildStatus = '';
            if (item.getStatus() !== BuildItem.BuildStatus.BUILD_STATUS_PASS) {
              if (item.getStatus() in BUILD_STATUS_MAPPINGS) {
                buildStatus = BUILD_STATUS_MAPPINGS[item.getStatus()];
              } else {
                // Gracefull fallback to Unknown status in case when
                // BuildItem.BuildStatus changes and this block is not
                // updated.
                buildStatus = 'Unknown';
              }
            } else if (item.getLabelsList().length !== 0 && item.getLabelsList().includes(labelName)) { // if buildVersion is labeled, set status to recommended
              buildStatus = BUILD_STATUS_MAPPINGS[BuildItem.BuildStatus.BUILD_STATUS_RECOMMENDED];
            }
            buildVersionNames.push({
              version: item.getValue(),
              status: buildStatus,
            });
          }
          callback(buildVersionNames, response.getIsIncomplete());
        }
      }
    );
  }

  listModels(
    callback: (x: string[]) => void,
    errorHandlingCallback: (err_msg: string) => void
  ) {
    const request = new ListModelsRequest();
    this.moblabRpcService.list_models(
      request,
      {},
      (err: grpcWeb.Error, response: ListModelsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getModelsList());
        }
      }
    );
  }

  async listAccessibleModelsPromise(buildTarget: string): Promise<Model[]> {
    /** Returns the models(s) that the account has access to as promise.
     * */
    const request = new ListAccessibleModelsRequest();
    request.setBuildTarget(buildTarget);
    const response = await this.moblabRpcServicePromiseClient.list_accessible_models(
      request
    );
    return response.getModelsList();
  }

  listPools(
    callback: (x: string[]) => void,
    errorHandlingCallback: (err_msg: string) => void,
    model: string | null,
  ) {
    const request = new ListPoolsRequest();
    request.setModel((model == null) ? "" : model)

    this.moblabRpcService.list_pools(
      request,
      {},
      (err: grpcWeb.Error, response: ListPoolsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getPoolsList());
        }
      }
    );
  }

  enrollDuts(
    ips: string[],
    callback: () => void,
    errorCallback: (msg: string) => void
  ) {
    const request = new EnrollDutsRequest();
    request.setIpsList(ips);
    this.moblabRpcService.enroll_duts(
      request,
      {},
      (err: grpcWeb.Error, response: EnrollDutsResponse) => {
        if (err) {
          errorCallback(err.message);
        } else {
          callback();
        }
      }
    );
  }

  unenrollDuts(
    ips: string[],
    callback: () => void,
    errorCallback: (msg: string) => void
  ) {
    const request = new EnrollDutsRequest();
    request.setIpsList(ips);
    this.moblabRpcService.unenroll_duts(
      request,
      {},
      (err: grpcWeb.Error, response: EnrollDutsResponse) => {
        if (err) {
          errorCallback(err.message);
        } else {
          callback();
        }
      }
    );
  }

  listConnectedDutsFirmware(callback: (x: ConnectedDutFirmwareInfo[]) => void) {
    const request = new ListConnectedDutsRequest();

    this.moblabRpcService.list_connected_duts_firmware(
      request,
      {},
      (err: grpcWeb.Error, response: ListConnectedDutsFirmwareResponse) => {
        if (err) {
          console.log(err);
        } else {
          console.log(response);
          callback(response.getDutsList());
        }
      }
    );
  }

  updateFirmwareOnDuts(
    ips: string[],
    callback: (x: FirmwareUpdateCommandOutput[]) => void
  ) {
    const request = new UpdateDutsFirmwareRequest();
    request.setIpsList(ips);
    this.moblabRpcService.update_duts_firmware(
      request,
      {},
      (err: grpcWeb.Error, response: UpdateDutsFirmwareResponse) => {
        if (err) {
          console.log(err);
        } else {
          callback(response.getOutputsList());
        }
      }
    );
  }

  getNumDutTasks(
    callback: (numDutTasks: number) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    ip: string,
    start_time_gt?: number,
    end_time_lt?: number
  ) {
    const request = new GetNumDutTasksRequest();
    request.setIp(ip);
    if (start_time_gt) {
      request.setStartTimeGt(start_time_gt);
    }
    if (end_time_lt) {
      request.setEndTimeLt(end_time_lt);
    }

    this.moblabRpcService.get_num_dut_tasks(
      request,
      {},
      (err: grpcWeb.Error, response: GetNumDutTasksResponse) => {
        if (err) {
          console.log(
            'Failed get_num_dut_actions RPC call. Request: ',
            request,
            'Response: ',
            err
          );
          errorHandlingCallback(err.message);
        } else {
          callback(response.getNumDutTasks());
        }
      }
    );
  }

  getDutTasks(
    callback: (x: DutTask[]) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    ip: string,
    queryStart: number,
    queryLimit: number,
    start_time_gt?: number,
    end_time_lt?: number
  ) {
    const request = new GetDutTasksRequest();
    request.setIp(ip);
    request.setQueryStart(queryStart);
    request.setQueryLimit(queryLimit);

    if (start_time_gt) {
      request.setStartTimeGt(start_time_gt);
    }
    if (end_time_lt) {
      request.setEndTimeLt(end_time_lt);
    }

    this.moblabRpcService.get_dut_tasks(
      request,
      {},
      (err: grpcWeb.Error, response: GetDutTasksResponse) => {
        if (err) {
          console.log(
            'Failed get_dut_actions RPC call. Request: ',
            request,
            'Response: ',
            err
          );
          errorHandlingCallback(err.message);
        } else {
          callback(response.getTasksList());
        }
      }
    );
  }

  repairDut(
    callback: (message: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut_hostname: string
  ) {
    const request = new RepairHostRequest();
    request.setDutHostname(dut_hostname);
    this.moblabRpcService.repair_host(
      request,
      {},
      (err: grpcWeb.Error, response: RepairHostResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  reverifyDuts(
    callback: (message: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut_hostnames: string[]
  ) {
    const request = new ReverifyHostRequest();
    request.setDutHostnamesList(dut_hostnames);
    this.moblabRpcService.reverify_host(
      request,
      {},
      (err: grpcWeb.Error, response: ReverifyHostResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  addAttributeToDuts(
    callback: (message: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut_ips: string[],
    key: string,
    value: string
  ) {
    const request = new AddAttributeToDutsRequest();
    request.setDutHostnamesList(dut_ips);
    request.setKey(key);
    request.setValue(value);

    this.moblabRpcService.add_attribute_to_duts(
      request,
      {},
      (err: grpcWeb.Error, response: AddAttributeToDutsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  removeAttributeFromDuts(
    callback: (message: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut_ips: string[],
    key: string
  ) {
    const request = new RemoveAttributeFromDutsRequest();
    request.setDutHostnamesList(dut_ips);
    request.setKey(key);
    this.moblabRpcService.remove_attribute_from_duts(
      request,
      {},
      (err: grpcWeb.Error, response: RemoveAttributeFromDutsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  addLabelToDuts(
    callback: (message: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut_ips: string[],
    label: string
  ) {
    const request = new AddLabelToDutsRequest();
    request.setDutHostnamesList(dut_ips);
    request.setLabel(label);
    this.moblabRpcService.add_label_to_duts(
      request,
      {},
      (err: grpcWeb.Error, response: AddLabelToDutsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  removeLabelFromDuts(
    callback: (message: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut_ips: string[],
    label: string
  ) {
    const request = new RemoveLabelFromDutsRequest();
    request.setDutHostnamesList(dut_ips);
    request.setLabel(label);
    this.moblabRpcService.remove_label_from_duts(
      request,
      {},
      (err: grpcWeb.Error, response: RemoveLabelFromDutsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  addPoolToDuts(
    callback: (message: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut_ips: string[],
    pool: string
  ) {
    /** Sends request to add pool label to given DUTs.
     *  @param callback: function invoked in success scenarios.
     *  @param error_callback: function invoked in failure scenarios.
     *  @param pool: Pool name to be associated with given DUT's
     *  @param dut_ips: Ip's of DUTs who will receive pool label.
     *  */
    const request = new AddPoolToDutsRequest();
    request.setDutHostnamesList(dut_ips);
    request.setPool(pool);
    this.moblabRpcService.add_pool_to_duts(
      request,
      {},
      (err: grpcWeb.Error, response: AddPoolToDutsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  removePoolFromDuts(
    callback: (message: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut_ips: string[],
    pool: string
  ) {
    /** Sends request to remove pool label to given DUTs.
     *  @param callback: function invoked in success scenarios.
     *  @param error_callback: function invoked in failure scenarios.
     *  @param pool: Pool name to be associated with given DUT's
     *  @param dut_ips: Ip's of DUTs who will have pool label removed.
     *  */
    const request = new RemovePoolFromDutsRequest();
    request.setDutHostnamesList(dut_ips);
    request.setPool(pool);
    this.moblabRpcService.remove_pool_from_duts(
      request,
      {},
      (err: grpcWeb.Error, response: RemovePoolFromDutsResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  get_network_info(
    callback: (
      moblab_hostname: string,
      moblab_mac_address: string,
      is_connected: boolean
    ) => void,
    errorHandlingCallback: (errorMsg: string) => void
  ) {
    const request = new GetNetworkInfoRequest();
    this.moblabRpcService.get_network_info(
      request,
      {},
      (err: grpcWeb.Error, response: GetNetworkInfoResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          console.log('NETWORK RESPONSE: ');
          console.log(response);
          callback(
            response.getMoblabHostname(),
            response.getMoblabMacAddress(),
            response.getIsConnected()
          );
        }
      }
    );
  }

  get_system_info(
    callback: (cpu_temperature: number) => void,
    errorHandlingCallback: (errorMsg: string) => void
  ) {
    const request = new GetSystemInfoRequest();
    this.moblabRpcService.get_system_info(
      request,
      {},
      (err: grpcWeb.Error, response: GetSystemInfoResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          console.log('SYSTEM INFO RESPONSE: ');
          console.log(response);
          callback(response.getCpuTemperature());
        }
      }
    );
  }

  get_cloud_configuration(
    callback: (
      boto_key_id: string,
      boto_key_secret: string,
      gcs_bucket_url: string,
      is_cloud_enabled: boolean,
      is_remote_console_enabled: boolean,
      is_remote_command_enabled: boolean
    ) => void,
    errorHandlingCallback: (errorMsg: string) => void
  ) {
    const request = new GetCloudConfigurationRequest();

    this.moblabRpcService.get_cloud_configuration(
      request,
      {},
      (err: grpcWeb.Error, response: GetCloudConfigurationResponse) => {
        if (err) {
          // Set Configuration alerting state before calling error handling
          // callback.
          this.configSetupService.setState(false, true);
          errorHandlingCallback(err.message);
        } else {
          // Set Configuration alerting state before calling success callback.
          this.configSetupService.setState(response.getIsCloudEnabled(), false);
          callback(
            response.getBotoKeyId(),
            response.getBotoKeySecret(),
            response.getGcsBucketUrl(),
            response.getIsCloudEnabled(),
            response.getIsRemoteConsoleEnabled(),
            response.getIsRemoteCommandEnabled()
          );
        }
      }
    );
  }

  set_cloud_configuration(
    callback: (message: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    boto_key_id: string,
    boto_key_secret: string,
    gcs_bucket_url: string,
    is_cloud_enabled: boolean,
    is_remote_console_enabled: boolean,
    is_remote_command_enabled: boolean
  ) {
    const request = new SetCloudConfigurationRequest();
    request.setBotoKeyId(boto_key_id);
    request.setBotoKeySecret(boto_key_secret);
    request.setGcsBucketUrl(gcs_bucket_url);
    request.setIsCloudEnabled(is_cloud_enabled);
    request.setIsRemoteConsoleEnabled(is_remote_console_enabled);
    request.setIsRemoteCommandEnabled(is_remote_command_enabled);

    this.moblabRpcService.set_cloud_configuration(
      request,
      {},
      (err: grpcWeb.Error, response: SetCloudConfigurationResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  get_dut_wifi_info(
    callback: (dut_wifi_name: string, dut_wifi_password: string) => void,
    errorHandlingCallback: (errorMsg: string) => void
  ) {
    const request = new GetDutWifiInfoRequest();

    this.moblabRpcService.get_dut_wifi_info(
      request,
      {},
      (err: grpcWeb.Error, response: GetDutWifiInfoResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getDutWifiName(), response.getDutWifiPassword());
        }
      }
    );
  }

  set_dut_wifi_info(
    callback: (message: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut_wifi_name: string,
    dut_wifi_password: string
  ) {
    const request = new SetDutWifiInfoRequest();
    request.setDutWifiName(dut_wifi_name);
    request.setDutWifiPassword(dut_wifi_password);

    this.moblabRpcService.set_dut_wifi_info(
      request,
      {},
      (err: grpcWeb.Error, response: SetDutWifiInfoResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  get_version_info(
    callback: (
      moblab_release_version: string,
      chromeos_release_version: string,
      chromeos_release_track: string,
      chromeos_release_description: string,
      moblab_install_id: string,
      moblab_serial_number: string
    ) => void,
    errorHandlingCallback: (errorMsg: string) => void
  ) {
    const request = new GetVersionInfoRequest();

    this.moblabRpcService.get_version_info(
      request,
      {},
      (err: grpcWeb.Error, response: GetVersionInfoResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(
            response.getMoblabReleaseVersion(),
            response.getChromeosReleaseVersion(),
            response.getChromeosReleaseTrack(),
            response.getChromeosReleaseDescription(),
            response.getMoblabInstallId(),
            response.getMoblabSerialNumber()
          );
        }
      }
    );
  }

  reboot_moblab(error_callback: (msg: string) => void) {
    this.moblabRpcService.reboot_moblab(
      new RebootMoblabRequest(),
      {},
      (err: grpcWeb.Error, response: RebootMoblabResponse) => {
        if (err) {
          error_callback(err.message);
        } else {
          console.log(response);
        }
      }
    );
  }

  get_is_update_available(
    /**
     * Get whether an update is available for the Moblab to pull.
     *  @param callback: function invoked in success scenarios.
     *  @param error_callback: function invoked in failure scenarios.
     *  */
    callback: (isUpdateAvailable: boolean) => void,
    error_callback: (msg: string) => void
  ) {
    this.moblabRpcService.get_is_update_available(
      new GetIsUpdateAvailableRequest(),
      {},
      (err: grpcWeb.Error, response: GetIsUpdateAvailableResponse) => {
        if (err) {
          error_callback(err.message);
        } else {
          callback(response.getIsUpdateAvailable());
        }
      }
    );
  }

  update_moblab(
    callback: (message: string) => void,
    error_callback: (msg: string) => void
  ) {
    /**
     *  Invoke a moblab update.
     *  @param callback: function invoked in success scenarios.
     *  @param error_callback: function invoked in failure scenarios.
     *  */
    this.moblabRpcService.update_moblab(
      new UpdateMoblabRequest(),
      {},
      (err: grpcWeb.Error, response: UpdateMoblabResponse) => {
        if (err) {
          error_callback(err.message);
        } else {
          callback(response.getMessage());
        }
      }
    );
  }

  /**
   *  Gets the Remote Agent configuration.
   *  @param callback: function invoked in success scenarios.
   *  @param error_callback: function invoked in failure scenarios.
   *  */
  get_remote_agent_configuration(
    callback: (is_enabled: boolean) => void,
    errorHandlingCallback: (errorMsg: string) => void
  ) {
    const request = new GetRemoteAgentConfigurationRequest();

    this.moblabRpcService.get_remote_agent_configuration(
      request,
      {},
      (err: grpcWeb.Error, response: GetRemoteAgentConfigurationResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getIsEnabled());
        }
      }
    );
  }

  /**
   *  Sets the Remote Agent configuration.
   *  @param callback: function invoked in success scenarios.
   *  @param error_callback: function invoked in failure scenarios.
   *  @param is_enabled: if remote agent is enabled or not.
   *  */
  set_remote_agent_configuration(
    callback: (is_succeeded: boolean) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    is_enabled: boolean
  ) {
    const request = new SetRemoteAgentConfigurationRequest();
    request.setIsEnabled(is_enabled);

    this.moblabRpcService.set_remote_agent_configuration(
      request,
      {},
      (err: grpcWeb.Error, response: SetRemoteAgentConfigurationResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response.getIsSucceeded());
        }
      }
    );
  }

  /**
   * Validate storage qual setup
   */
  validateStorageQualSetup(
    callback: () => void,
    errorHandlingCallback: (errorMsg: string) => void,
    model: string,
    board: string,
    pool_name: string = null,
  ) {
    const request = new ValidateStorageQualSetupRequest();
    request.setModel(model);
    request.setBoard(board);
    request.setPoolName(pool_name);

    this.moblabRpcService.validate_storage_qual_setup(
      request,
      {},
      (err: grpcWeb.Error, _) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback();
        }
      }
    );
  }

  addServo(
    callback: () => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut_hostname: string,
    servo_serial_number: string
  ) {
    const request = new AddServoRequest();
    request.setDutHostname(dut_hostname);
    request.setServoSerialNumber(servo_serial_number);
    this.moblabRpcService.add_servo(
      request,
      {},
      (err: grpcWeb.Error, response: AddServoResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback();
        }
      }
    );
  }

  async getCloudBucketUrl(): Promise<string> {
    const version = await new Promise<string>((resolve, reject) => {
      this.get_version_info(
        (
          _moblab_release_version: string,
          _chromeos_release_version: string,
          _chromeos_release_track: string,
          _chromeos_release_description: string,
          moblab_install_id: string,
          moblab_serial_number: string
        ) => {
          resolve(`${moblab_serial_number}/${moblab_install_id}`);
        },
        (errorMsg: string) => {
          reject(errorMsg);
        }
      );
    });

    const bucket = await new Promise<string>((resolve, reject) => {
      this.get_cloud_configuration(
        (
          _boto_key_id: string,
          _boto_key_secret: string,
          gcs_bucket_url: string,
          _is_cloud_enabled: boolean,
          _is_remote_console_enabled: boolean,
          _is_remote_command_enabled: boolean
        ) => {
          if (gcs_bucket_url && gcs_bucket_url.startsWith('gs://'))
            resolve(gcs_bucket_url.substr(5));
        },
        (errorMsg: string) => reject(errorMsg)
      );
    });

    return `https://console.cloud.google.com/storage/browser/${bucket}results/${version}`;
  }

  getPeripheralInformation(
    dut_ip : string,
    callback: (x: GetPeripheralInformationResponse) => void,
    errorHandlingCallback: (errorMsg: string) => void,
  ){
      const request = new GetPeripheralInformationRequest()
      request.setDutHostname(dut_ip)
      this.moblabRpcService.get_peripheral_information(
        request, 
        {}, 
        (err: grpcWeb.Error, response: GetPeripheralInformationResponse) => {
        if (err) {
          errorHandlingCallback(err.message);
        } else {
          callback(response);
        }
      }
      )
  }
}
