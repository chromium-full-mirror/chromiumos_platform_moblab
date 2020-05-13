import {Injectable} from "@angular/core";
import * as grpcWeb from "grpc-web";

import {MoblabRpcServiceClient} from "./moblabrpc_grpc_web_pb";
import {
  AbortJobsRequest,
  AbortJobsResponse,
  AddAttributeToDutsRequest,
  AddAttributeToDutsResponse,
  AddLabelToDutsRequest,
  AddLabelToDutsResponse,
  ConnectedDutFirmwareInfo,
  ConnectedDutInfo,
  DutTask,
  EnrollDutsRequest,
  EnrollDutsResponse,
  GetDutDetailsRequest,
  GetDutDetailsResponse,
  GetDutTasksRequest,
  GetDutTasksResponse,
  GetJobDetailsRequest,
  GetJobDetailsResponse,
  GetJobsRequest,
  GetJobsResponse,
  GetNumDutTasksRequest,
  GetNumDutTasksResponse,
  GetNumJobsRequest,
  GetNumJobsResponse,
  Job,
  ListBuildTargetsRequest,
  ListBuildTargetsResponse,
  ListBuildVersionsRequest,
  ListBuildVersionsResponse,
  ListConnectedDutsFirmwareResponse,
  ListConnectedDutsRequest,
  ListConnectedDutsResponse,
  ListMilestonesRequest,
  ListMilestonesResponse,
  ListModelsRequest,
  ListModelsResponse,
  ListPoolsRequest,
  ListPoolsResponse,
  RemoveAttributeFromDutsRequest,
  RemoveAttributeFromDutsResponse,
  RemoveLabelFromDutsRequest,
  RemoveLabelFromDutsResponse,
  RepairHostRequest,
  RepairHostResponse,
  ReverifyHostRequest,
  ReverifyHostResponse,
  RunCtsSuiteRequest,
  RunCtsSuiteResponse,
  RunGtsSuiteRequest,
  RunMemoryQualificationSuiteRequest,
  RunStorageQualificationSuiteRequest,
  RunSuiteRequest,
  RunSuiteResponse,
  SendMoblabScreenshotRequest,
  SendMoblabScreenshotResponse,
  UpdateDutsFirmwareRequest,
  UpdateDutsFirmwareResponse
} from "./moblabrpc_pb";

@Injectable({providedIn: "root"})
export class MoblabGrpcService {
  moblabRpcService = null;

  constructor() {
    let url = new URL(window.location.href);
    let service_url = new String(url.protocol);
    service_url = service_url.concat("//", url.hostname, ":", "6001");
    console.log(service_url);

    this.moblabRpcService = new MoblabRpcServiceClient(
      service_url.toString(),
      null,
      null
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
    description,
    screenshot
  ) {
    const request = new SendMoblabScreenshotRequest();
    request.setDescription(description);
    request.setScreenshot(screenshot.substring(screenshot.indexOf(',') + 1));

    const call = this.moblabRpcService.send_moblab_screenshot(
      request,
      {},
      (response) => {error_callback(response.message);}
    );
    call.on("data", (response) => {callback(response.getMessage())});
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
    buildtarget: string,
    model: string,
    pool: string,
  ) {
    const request = new RunSuiteRequest();
    request.setSuite(suite_name);
    request.setBuildVersion(build);
    request.setBuildTarget(buildtarget);
    request.setModel(model);
    request.setPool(pool);

    const call = this.moblabRpcService.run_suite(
      request,
      {},
      error_callback
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
    callback: (response: RunCtsSuiteResponse) => void,
    error_callback: (err: grpcWeb.Error, response: RunCtsSuiteResponse) => void,
    android_version: string,
    build: string,
    buildtarget: string,
    model: string,
    pool: string,
    specific_modules_list: string[],
  ) {
    const request = new RunCtsSuiteRequest();
    request.setAndroidVersion(android_version);
    request.setBuildVersion(build);
    request.setBuildTarget(buildtarget);
    request.setModel(model);
    request.setPool(pool);
    request.setSpecificModulesList(specific_modules_list);

    const call = this.moblabRpcService.run_cts_suite(
      request,
      {},
      error_callback
    );

    call.on("data", callback);
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
    buildtarget: string,
    model: string,
    pool: string,
    specific_modules_list: string[],
  ) {
    const request = new RunGtsSuiteRequest();
    request.setBuildVersion(build);
    request.setBuildTarget(buildtarget);
    request.setModel(model);
    request.setPool(pool);
    request.setSpecificModulesList(specific_modules_list);

    const call = this.moblabRpcService.run_gts_suite(
      request,
      {},
      error_callback
    );

    call.on("data", callback);
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
   *  */
  runStorageQualificationSuite(
    callback: (response: RunSuiteResponse) => void,
    error_callback: (err: grpcWeb.Error, response: RunSuiteResponse) => void,
    build: string,
    buildtarget: string,
    model: string,
    pool: string,
    avl_process_bug_id: number,
    avl_part_number: string
  ) {
    const request = new RunStorageQualificationSuiteRequest();
    request.setBuildVersion(build);
    request.setBuildTarget(buildtarget);
    request.setModel(model);
    request.setPool(pool);
    request.setAvlProcessBugId(avl_process_bug_id);
    request.setAvlPartNumber(avl_part_number);

    const call = this.moblabRpcService.run_storage_qualification_suite(
      request,
      {},
      error_callback
    );

    call.on("data", callback);
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
    buildtarget: string,
    model: string,
    suite: string,
    pool: string,
    avl_process_bug_id: number,
    avl_part_number: string
  ) {
    const request = new RunMemoryQualificationSuiteRequest();
    request.setBuildVersion(build);
    request.setBuildTarget(buildtarget);
    request.setModel(model);
    request.setPool(pool);
    request.setAvlProcessBugId(avl_process_bug_id);
    request.setAvlPartNumber(avl_part_number);

    const call = this.moblabRpcService.run_memory_qualification_suite(
      request,
      {},
      error_callback
    );

    call.on("data", callback);
  }

  listConnectedDuts(callback: (x: ConnectedDutInfo[]) => void) {
    const request = new ListConnectedDutsRequest();

    const call = this.moblabRpcService.list_connected_duts(
      request,
      {},
      (err: grpcWeb.Error, response: ListConnectedDutsResponse) => {
        console.log(err);
      }
    );

    call.on("data", (response: ListConnectedDutsResponse) => {
      callback(response.getDutsList());
    });
  }

  getDutDetails(callback: (x: ConnectedDutInfo) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    dut: string) {
    const request = new GetDutDetailsRequest();
    request.setDut(dut);

    const call = this.moblabRpcService.get_dut_details(
      request,
      {},
      (err: grpcWeb.Error, response: GetDutDetailsResponse) => {
        console.log(
          "Failed get_dut_details RPC call. Request: ",
          request,
          "Response: ",
          err
        );
        errorHandlingCallback(err.message);
      }
    );
    call.on("data", (response: GetDutDetailsResponse) => {
      callback(response.getDutDetail());
    });
  }

  getNumJobs(callback: (x: number) => void,
    id_filter?: string,
    name_filter?: string, created_time_lt?: number, created_time_gt?: number,
    status_filter?: Job.QueueStatus, rel_filter?: Job.Relationship,
    parent_id_filter?: string, dut_hostname_filter?: string) {
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

    const call = this.moblabRpcService.get_num_jobs(
      request,
      {},
      (err: grpcWeb.Error, response: GetNumJobsResponse) => {
        console.log(
          "Failed get_num_jobs RPC call. Request: ",
          request,
          "Response: ",
          err
        );
      }
    );
    call.on("data", (response: GetNumJobsResponse) => {
      callback(response.getNumJobs());
    });
  }

  getJobs(callback: (x: Job[]) => void,
    queryStart: number, queryLimit: number, id_filter?: string,
    name_filter?: string, created_time_lt?: number, created_time_gt?: number,
    status_filter?: Job.QueueStatus, rel_filter?: Job.Relationship,
    parent_id_filter?: string, dut_hostname_filter?: string) {
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

    const call = this.moblabRpcService.get_jobs(
      request,
      {},
      (err: grpcWeb.Error, response: GetJobsResponse) => {
        console.log(
          "Failed get_num_jobs RPC call. Request: ",
          request,
          "Response: ",
          err
        );
      }
    );
    call.on("data", (response: GetJobsResponse) => {
      callback(response.getJobsList());
    });
  }

  abortJobs(callback: (message: string) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    jobIds: number[]) {
    const request = new AbortJobsRequest();
    request.setJobIdsList(jobIds);

    const call = this.moblabRpcService.abort_jobs(
      request,
      {},
      (err: grpcWeb.Error, response: AbortJobsResponse) => {
        console.log(
          "Failed abort jobs RPC call. Request: ",
          request,
          "Response: ",
          err
        );
        errorHandlingCallback(err.message);
      }
    );
    call.on("data", (response: AbortJobsResponse) => {
      callback(response.getMessage());
    });
  }

  getJobDetails(callback: (x: Job) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    id: string) {
    const request = new GetJobDetailsRequest();
    request.setId(id);

    const call = this.moblabRpcService.get_job_details(
      request,
      {},
      (err: grpcWeb.Error, response: GetJobDetailsResponse) => {
        console.log(
          "Failed get_job_details RPC call. Request: ",
          request,
          "Response: ",
          err
        );
        errorHandlingCallback(err.message);
      }
    );
    call.on("data", (response: GetJobDetailsResponse) => {
      callback(response.getJobDetail());
    });
  }

  listBuildTargets(callback: (x: string[]) => void) {
    const request = new ListBuildTargetsRequest();

    const call = this.moblabRpcService.list_build_targets(
      request,
      {},
      (err: grpcWeb.Error, response: ListBuildTargetsResponse) => {
        console.log(err);
      }
    );
    call.on("data", (response: ListBuildTargetsResponse) => {
      console.log(response);
      callback(response.getBuildTargetsList());
    });
  }

  listMilestones(buildtarget: string, callback: (x: string[]) => void) {
    const request = new ListMilestonesRequest();
    request.setBuildTarget(buildtarget);

    const call = this.moblabRpcService.list_milestones(
      request,
      {},
      (err: grpcWeb.Error, response: ListMilestonesResponse) => {
        console.log(err);
      }
    );
    call.on("data", (response: ListMilestonesResponse) => {
      callback(response.getMilestonesList());
    });
  }

  listBuildVersions(
    buildtarget: string,
    milestone: string,
    callback: (x: string[]) => void
  ) {
    const request = new ListBuildVersionsRequest();
    request.setBuildTarget(buildtarget);
    request.setMilestone(milestone);

    const call = this.moblabRpcService.list_build_versions(
      request,
      {},
      (err: grpcWeb.Error, response: ListBuildVersionsResponse) => {
        console.log(err);
      }
    );
    call.on("data", (response: ListBuildVersionsResponse) => {
      callback(response.getBuildVersionsList());
    });
  }

  listModels(callback: (x: string[]) => void) {
    const request = new ListModelsRequest();

    const call = this.moblabRpcService.list_models(
      request,
      {},
      (err: grpcWeb.Error, response: ListModelsResponse) => {
        console.log(err);
      }
    );
    call.on("data", (response: ListModelsResponse) => {
      callback(response.getModelsList());
    });
  }

  listPools(callback: (x: string[]) => void) {
    const request = new ListPoolsRequest();

    const call = this.moblabRpcService.list_pools(
      request,
      {},
      (err: grpcWeb.Error, response: ListPoolsResponse) => {
        console.log(err);
      }
    );
    call.on("data", (response: ListPoolsResponse) => {
      callback(response.getPoolsList());
    });
  }

  enrollDuts(ips: string[], callback: () => void) {
    const request = new EnrollDutsRequest();
    request.setIpsList(ips);
    const call = this.moblabRpcService.enroll_duts(
      request,
      {},
      (err: grpcWeb.Error, response: EnrollDutsResponse) => {
        console.log(err);
      }
    );
    call.on("data", (response: EnrollDutsResponse) => {
      callback();
    });
  }

  unenrollDuts(ips: string[], callback: () => void) {
    const request = new EnrollDutsRequest();
    request.setIpsList(ips);
    const call = this.moblabRpcService.unenroll_duts(
      request,
      {},
      (err: grpcWeb.Error, response: EnrollDutsResponse) => {
        console.log(err);
      }
    );
    call.on("data", (response: EnrollDutsResponse) => {
      callback();
    });
  }

  listConnectedDutsFirmware(callback: (x: ConnectedDutFirmwareInfo[]) => void) {
    const request = new ListConnectedDutsRequest();

    const call = this.moblabRpcService.list_connected_duts_firmware(
      request,
      {},
      (err: grpcWeb.Error, response: ListConnectedDutsFirmwareResponse) => {
        console.log(err);
      }
    );
    call.on("data", (response: ListConnectedDutsFirmwareResponse) => {
      console.log(response);
      callback(response.getDutsList());
    });
  }

  updateFirmwareOnDuts(ips: string[], callback: () => void) {
    const request = new UpdateDutsFirmwareRequest();
    request.setIpsList(ips);
    const call = this.moblabRpcService.update_duts_firmware(
      request,
      {},
      (err: grpcWeb.Error, response: UpdateDutsFirmwareResponse) => {
        console.log(err);
      }
    );
    call.on("data", (response: UpdateDutsFirmwareResponse) => {
      callback();
    });
  }

  getNumDutTasks(callback: (numDutTasks: number) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    ip: string, start_time_gt?: number, end_time_lt?: number) {
    const request = new GetNumDutTasksRequest();

    if (start_time_gt) {
      request.setStartTimeGt(start_time_gt);
    }
    if (end_time_lt) {
      request.setEndTimeLt(end_time_lt);
    }

    const call = this.moblabRpcService.get_num_dut_tasks(
      request,
      {},
      (err: grpcWeb.Error, response: GetNumDutTasksResponse) => {
        console.log(
          "Failed get_num_dut_actions RPC call. Request: ",
          request,
          "Response: ",
          err
        );
        errorHandlingCallback(err.message);
      }
    );
    call.on("data", (response: GetNumDutTasksResponse) => {
      callback(response.getNumDutTasks());
    });
  }

  getDutTasks(callback: (x: DutTask[]) => void,
    errorHandlingCallback: (errorMsg: string) => void,
    ip: string, queryStart: number, queryLimit: number,
    start_time_gt?: number, end_time_lt?: number) {
    const request = new GetDutTasksRequest();
    request.setQueryStart(queryStart);
    request.setQueryLimit(queryLimit);

    if (start_time_gt) {
      request.setStartTimeGt(start_time_gt);
    }
    if (end_time_lt) {
      request.setEndTimeLt(end_time_lt);
    }

    const call = this.moblabRpcService.get_dut_tasks(
      request,
      {},
      (err: grpcWeb.Error, response: GetDutTasksResponse) => {
        console.log(
          "Failed get_dut_actions RPC call. Request: ",
          request,
          "Response: ",
          err
        );
        errorHandlingCallback(err.message);
      }
    );
    call.on("data", (response: GetDutTasksResponse) => {
      callback(response.getTasksList());
    });
  }

  repairDut(callback: (message: string) => void, errorHandlingCallback: (errorMsg: string) => void,
    dut_hostname: string) {
    const request = new RepairHostRequest();
    request.setDutHostname(dut_hostname);
    const call = this.moblabRpcService.repair_host(
      request,
      {},
      (err: grpcWeb.Error, response: RepairHostResponse) => {
        errorHandlingCallback(err.message);
      }
    );
    call.on("data", (response: RepairHostResponse) => {
      callback(response.getMessage());
    });
  }

  reverifyDut(callback: (message: string) => void, errorHandlingCallback: (errorMsg: string) => void,
    dut_hostname: string) {
    const request = new ReverifyHostRequest();
    request.setDutHostname(dut_hostname);
    const call = this.moblabRpcService.reverify_host(
      request,
      {},
      (err: grpcWeb.Error, response: ReverifyHostResponse) => {
        errorHandlingCallback(err.message);
      }
    );
    call.on("data", (response: ReverifyHostResponse) => {
      callback(response.getMessage());
    });
  }

  addAttributeToDuts(callback: (message: string) => void, errorHandlingCallback: (errorMsg: string) => void,
    dut_ips: string[], key: string, value: string) {
    const request = new AddAttributeToDutsRequest();
    request.setDutHostnamesList(dut_ips);
    request.setKey(key);
    request.setValue(value);

    const call = this.moblabRpcService.add_attribute_to_duts(
      request,
      {},
      (err: grpcWeb.Error, response: AddAttributeToDutsResponse) => {
        errorHandlingCallback(err.message);
      }
    );
    call.on("data", (response: AddAttributeToDutsResponse) => {
      callback(response.getMessage());
    });
  }

  removeAttributeFromDuts(callback: (message: string) => void, errorHandlingCallback: (errorMsg: string) => void,
    dut_ips: string[], key: string) {
    const request = new RemoveAttributeFromDutsRequest();
    request.setDutHostnamesList(dut_ips);
    request.setKey(key);
    const call = this.moblabRpcService.remove_attribute_from_duts(
      request,
      {},
      (err: grpcWeb.Error, response: RemoveAttributeFromDutsResponse) => {
        errorHandlingCallback(err.message);
      }
    );
    call.on("data", (response: RemoveAttributeFromDutsResponse) => {
      callback(response.getMessage());
    });
  }

  addLabelToDuts(callback: (message: string) => void, errorHandlingCallback: (errorMsg: string) => void,
    dut_ips: string[], label: string) {
    const request = new AddLabelToDutsRequest();
    request.setDutHostnamesList(dut_ips);
    request.setLabel(label);
    const call = this.moblabRpcService.add_label_to_duts(
      request,
      {},
      (err: grpcWeb.Error, response: AddLabelToDutsResponse) => {
        errorHandlingCallback(err.message);
      }
    );
    call.on("data", (response: AddLabelToDutsResponse) => {
      callback(response.getMessage());
    });
  }

  removeLabelFromDuts(callback: (message: string) => void, errorHandlingCallback: (errorMsg: string) => void,
    dut_ips: string[], label: string) {
    const request = new RemoveLabelFromDutsRequest();
    request.setDutHostnamesList(dut_ips);
    request.setLabel(label);
    const call = this.moblabRpcService.remove_label_from_duts(
      request,
      {},
      (err: grpcWeb.Error, response: RemoveLabelFromDutsResponse) => {
        errorHandlingCallback(err.message);
      }
    );
    call.on("data", (response: RemoveLabelFromDutsResponse) => {
      callback(response.getMessage());
    });
  }
}
