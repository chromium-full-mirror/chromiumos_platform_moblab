import {Injectable} from '@angular/core';
import {BehaviorSubject, Observable} from 'rxjs';
import {ConnectedDutInfo} from 'app/services/moblabrpc_pb';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {NotificationsService} from 'app/services/notifications.service';

@Injectable({
  providedIn: 'root',
})
export class BuildTargetAccessService {
  modelsWithoutAccessObservable: Observable<string[]>;
  buildTargetsObservable: Observable<string[]>;
  private modelsWithoutAccessSubject: BehaviorSubject<string[]>;
  private buildTargetSubject: BehaviorSubject<string[]>;
  private buildTargets: string[] = [];

  constructor(
    private moblabGrpcService: MoblabGrpcService,
    private notificationsService: NotificationsService
  ) {
    this.modelsWithoutAccessSubject = new BehaviorSubject<string[]>([]);
    this.buildTargetSubject = new BehaviorSubject<string[]>([]);
    this.modelsWithoutAccessObservable = this.modelsWithoutAccessSubject.asObservable();
    this.buildTargetsObservable = this.buildTargetSubject.asObservable();
    this.initModelsWithoutAccess();
  }

  public updateModelsWithoutAccess(connectedDuts: ConnectedDutInfo[]) {
    if (this.buildTargets.length === 0) {
      return;
    }

    const enrolledDuts = connectedDuts.filter(connectedDut =>
      connectedDut.getIsEnrolled()
    );
    const modelsWithoutAccess = enrolledDuts
      .filter(dut => !this.buildTargets.includes(dut.getBuildTarget()))
      .map(dut => dut.getModel());
    this.modelsWithoutAccessSubject.next([...new Set(modelsWithoutAccess)]);
  }

  private async initModelsWithoutAccess() {
    await this.getBuildTargets();
    this.getConnectedDuts();
  }

  private async getBuildTargets() {
    try {
      this.buildTargets = await this.moblabGrpcService.listBuildTargetsPromise();
      this.buildTargetSubject.next(this.buildTargets);
    } catch (error) {
      this.notificationsService.error(error);
    }
  }

  private getConnectedDuts() {
    this.moblabGrpcService.listConnectedDuts(
      (connectedDuts: ConnectedDutInfo[]) => {
        this.updateModelsWithoutAccess(connectedDuts);
      },
      (message: string) => {
        this.notificationsService.error(message);
      }
    );
  }
}
