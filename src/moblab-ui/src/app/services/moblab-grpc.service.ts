import * as grpcWeb from 'grpc-web';

import { MoblabRpcServiceClient } from './moblabrpc_grpc_web_pb';
import {
  RunSuiteRequest,
  RunSuiteResponse,
  ConnectedDutInfo,
  ListConnectedDutsRequest,
  ListConnectedDutsResponse,
  ListBoardsRequest,
  ListBoardsResponse,
  ListMilestonesRequest,
  ListMilestonesResponse,
  ListBuildsRequest,
  ListBuildsResponse,
  ListModelsRequest,
  ListModelsResponse,
  ListPoolsRequest,
  ListPoolsResponse,
  RunCtsSuiteRequest,
  RunCtsSuiteResponse,
  EnrollDutsRequest,
  EnrollDutsResponse,
  ListConnectedDutsFirmwareResponse,
  ConnectedDutFirmwareInfo
} from './moblabrpc_pb';

import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class MoblabGrpcService {
  moblabRpcService = new MoblabRpcServiceClient(
    'http://localhost:6001',
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

    // call.on('data', (response: Response) => { console.log(response.getMessage()); callback(response.getMessage());});
    callback('Hello');
  }

  runCtsSuite(build: string, board: string, model: string, suite: string, pool: string, autotest_tests: string, tradefed_tests: string) {
    const request = new RunCtsSuiteRequest();
    request.setBuild(build);
    request.setBoard(board);
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

    call.on('data', (response: RunCtsSuiteResponse) => {
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

    call.on('data', (response: ListConnectedDutsResponse) => {
      callback(response.getDutsList());
    });
  }

  listBoards(callback: (x: string[]) => void) {

    const request = new ListBoardsRequest();

    const call = this.moblabRpcService.list_boards(
      request,
      {},
      (err: grpcWeb.Error, response: ListBoardsResponse) => {
        console.log(err);
      }
    );
    call.on('data', (response: ListBoardsResponse) => {
      console.log(response); callback(response.getBoardsList());
    });
  }

  listMilestones(board: string, callback: (x: string[]) => void) {
    const request = new ListMilestonesRequest();
    request.setBoard(board);

    const call = this.moblabRpcService.list_milestones(
      request,
      {},
      (err: grpcWeb.Error, response: ListMilestonesResponse) => {
        console.log(err);
      }
    );
    call.on('data', (response: ListMilestonesResponse) => {
      callback(response.getMilestonesList());
    });
  }

  listBuilds(board: string, milestone: string, callback: (x: string[]) => void) {
    const request = new ListBuildsRequest();
    request.setBoard(board);
    request.setMilestone(milestone);

    const call = this.moblabRpcService.list_builds(
      request,
      {},
      (err: grpcWeb.Error, response: ListBuildsResponse) => {
        console.log(err);
      }
    );
    call.on('data', (response: ListBuildsResponse) => {
      callback(response.getBuildsList());
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
    call.on('data', (response: ListModelsResponse) => {
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
    call.on('data', (response: ListPoolsResponse) => {
      callback(response.getPoolsList());
    });
  }

  enrollDuts(ips: string[], callback: () => void) {
    const request = new EnrollDutsRequest();
    request.setIpsList(ips)
    const call = this.moblabRpcService.enroll_duts(
      request,
      {},
      (err: grpcWeb.Error, response: EnrollDutsResponse) => {
        console.log(err);
      }
    );
    call.on('data', (response: EnrollDutsResponse) => {
      callback();
    });
  }

  unenrollDuts(ips: string[], callback: () => void) {
    const request = new EnrollDutsRequest();
    request.setIpsList(ips)
    const call = this.moblabRpcService.unenroll_duts(
      request,
      {},
      (err: grpcWeb.Error, response: EnrollDutsResponse) => {
        console.log(err);
      }
    );
    call.on('data', (response: EnrollDutsResponse) => {
      callback();
    });
  }

  listConnectedDutsFirmware (callback: (x: ConnectedDutFirmwareInfo[]) => void) {
    const request = new ListConnectedDutsRequest();

    const call = this.moblabRpcService.list_connected_duts_firmware(
      request,
      {},
      (err: grpcWeb.Error, response: ListConnectedDutsFirmwareResponse) => {
        console.log(err);
      }
    );
    call.on('data', (response: ListConnectedDutsFirmwareResponse) => {
      console.log(response);
      callback(response.getDutsList());
    });
  }


}
