import {Injectable} from "@angular/core";
import {Observable} from "rxjs";

@Injectable()
export class MoblabRpcServiceMock {

  private createMockObservable(data) : Observable<string> {
    return Observable.from([data]).flatMap(
        value => Observable.timer(1),
        value => value
    );
  }

  getBoards(): Observable<string> {
    return this.createMockObservable(["cyan", "veyron_minnie"]);
  }

  getBuilds(board: string): Observable<string> {
    return this.createMockObservable(["build1", "build2"]);
  }

  getFirmwareBuilds(board: string): Observable<string> {
    return this.createMockObservable(["firmware1", "firmware2"]);
  }

  getPools(): Observable<string> {
    return this.createMockObservable(["pool1", "pool2"]);
  }

  runSuite(board: string, build: string, suite: string, pool: string, rw_firmware: string,
           ro_firmware: string){
    console.log("run_suite", {"board": board, "build": build, "suite": suite,
      "pool": pool, "rw_firmware": rw_firmware, "ro_firmware": ro_firmware});
    return this.createMockObservable(null);
  }
}
