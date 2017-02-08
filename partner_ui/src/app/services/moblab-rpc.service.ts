import { Injectable } from '@angular/core';
import {Http, Response, Headers, RequestMethod} from '@angular/http';
import 'rxjs/Rx';
import {Observable} from "rxjs";

@Injectable()
export class MoblabRpcService {

  constructor(private http: Http) { }

  sendRpcCall(method, params): Observable<string> {

  var headers = new Headers();
  headers.append('Content-Type','text/plain');

    var content = JSON.stringify({
      method: method,
      params: [params],
      id: 0
    });

    // TODO(haddowk) mock out the RPC service for UI developement rather than using a local server.
    //return this.http.post("http://" + window.location.hostname + "/afe/server/rpc/", content,
    return this.http.post("http://" + "100.96.49.226" + "/afe/server/rpc/", content,
      {headers: headers, method: RequestMethod.Post, withCredentials: true})
    .map((res:Response) => res.json().result)
    .catch((error: any) => {
      return Observable.throw(error.json().error || 'Server error');
    });
  }

  getBoards(): Observable<string> {
    return this.sendRpcCall("get_connected_boards", {});
  }

  getBuilds(board: string): Observable<string> {
    return this.sendRpcCall("get_builds_for_board", {"board_name": board});
  }

  getFirmwareBuilds(board: string): Observable<string> {
    return this.sendRpcCall("get_firmware_for_board", {"board_name": board});
  }

  getPools(): Observable<string> {
    return this.sendRpcCall("get_connected_pools", {});
  }

  runSuite(board: string, build: string, suite: string, pool: string, rw_firmware: string,
           ro_firmware: string){
    return this.sendRpcCall("run_suite", {"board": board, "build": build, "suite": suite,
      "pool": pool, "rw_firmware": rw_firmware, "ro_firmware": ro_firmware});
  }
}
