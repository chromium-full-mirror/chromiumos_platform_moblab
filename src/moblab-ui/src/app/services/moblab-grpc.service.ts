import { Injectable } from "@angular/core";
import * as grpcWeb from "grpc-web";

import { MoblabRpcServiceClient } from "./moblabrpc_grpc_web_pb";
import {
  ConnectedDutFirmwareInfo,
  ConnectedDutInfo,
  EnrollDutsRequest,
  EnrollDutsResponse,
  GetJobsRequest,
  GetJobsResponse,
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
  RunCtsSuiteRequest,
  RunCtsSuiteResponse,
  RunSuiteRequest,
  RunSuiteResponse,
  UpdateDutsFirmwareRequest,
  UpdateDutsFirmwareResponse
} from "./moblabrpc_pb";

@Injectable({ providedIn: "root" })
export class MoblabGrpcService {
  moblabRpcService = new MoblabRpcServiceClient(
    "http://localhost:6001",
    null,
    null
  );

  constructor() {}

  runSuite(name: string, callback: (x: string) => void) {
    // const request = new RunSuiteRequest();
    // request.setName(name);

    // const call = this.moblabRpcService.run_suite(request, {},
    //   (err: grpcWeb.Error, response: Response) => {
    //   callback("RPC Error");
    // });

    // call.on('data', (response: Response) => {
    // console.log(response.getMessage()); callback(response.getMessage());});
    callback("Hello");
  }

  runCtsSuite(
    build: string,
    buildtarget: string,
    model: string,
    suite: string,
    pool: string,
    autotest_tests: string,
    tradefed_tests: string
  ) {
    const request = new RunCtsSuiteRequest();
    request.setBuildVersion(build);
    request.setBuildTarget(buildtarget);
    request.setModel(model);
    request.setSuite(suite);
    request.setPool(pool);
    const call = this.moblabRpcService.run_cts_suite(
      request,
      {},
      (err: grpcWeb.Error, response: RunCtsSuiteResponse) => {
        console.log(err);
      }
    );

    call.on("data", (response: RunCtsSuiteResponse) => {
      console.log(response.getMessage());
    });
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
      callback(
        response.getDutsList()
      );
    });
  }

  getJobs(callback: (x: Job[]) => void) {
    const request = new GetJobsRequest();
    const call = this.moblabRpcService.get_jobs(
      request,
      {},
      (err: grpcWeb.Error, response: GetJobsResponse) => {
        console.log(err);
      }
    );
    call.on("data", (response: GetJobsResponse) => {
      callback([]);
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
}
