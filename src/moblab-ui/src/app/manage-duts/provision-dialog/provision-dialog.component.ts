import {AfterViewInit, Component, Inject, ViewChild} from '@angular/core';
import {MAT_DIALOG_DATA} from '@angular/material/dialog';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {LoadingOverlayComponent, LoadingOverlayStyle} from 'app/widgets/loading-overlay/loading-overlay.component';
import {ConnectedDutInfo} from 'app/services/moblabrpc_pb';

export interface DialogData {
  milestone: string;
  buildVersion: string;
  pool: string;
}

@Component({
  selector: 'app-provision-dialog',
  templateUrl: 'provision-dialog.component.html',
  styleUrls: ['provision-dialog.component.scss']
})
export class ProvisionDialogComponent implements AfterViewInit {
  @ViewChild('buildSelector') buildSelector;
  @ViewChild('milestoneSelector') milestoneSelector;
  @ViewChild('poolSelector') poolSelector;
  @ViewChild(LoadingOverlayComponent) loadingOverlay: LoadingOverlayComponent;

  milestones: string[] = [];
  buildVersions: string[] = [];
  pools: string[] = [];

  build: DialogData = {milestone: "", buildVersion: "", pool: ""};

  private model = "";
  private board = "";
  public canStart = false

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: {duts: ConnectedDutInfo[]},
    private moblabGrpcService: MoblabGrpcService) {
  }

  ngAfterViewInit() {
    this.loadPools();
  }

  loadPools(): void {
    this.resetPools();
    this.loadingOverlay.updateStatus("Loading pools ...", LoadingOverlayStyle.Top)
    this.moblabGrpcService.listPools(
      (pools) => {
        pools.push("<all>");
        this.updatePools(pools);
        this.loadingOverlay.hide();
      },
      (errorMessage) => {this.showErrorMessage(errorMessage);}
    );
  }

  resetPools() {
    this.pools = [];
    this.poolSelector.disable("loading...");
    this.resetMilestones("Please select pool.");
  }

  updatePools(pools: string[]) {
    this.pools = pools;
    this.poolSelector.enable();
  }

  poolChanged(pool: string): void {
    if (pool == "<all>") {
      pool = "";
    }
    this.build.pool = pool;
    const chosenDut = this.data.duts.find(d => !pool || pool in d.getPoolsList());
    this.model = chosenDut.getModel();
    this.board = chosenDut.getBuildTarget();
    this.loadMilestones();
  }

  loadMilestones(): void {
    this.resetMilestones("loading...");
    this.loadingOverlay.updateStatus("Loading milestones ...", LoadingOverlayStyle.Top)
    this.moblabGrpcService.listMilestones(
      this.board,
      this.model,
      (milestones, _) => {
        this.updateMilestones(milestones);
        this.loadingOverlay.hide();
      },
      (errorMessage) => {this.showErrorMessage(errorMessage);}
    );
  }

  resetMilestones(message: string) {
    this.milestones = [];
    this.milestoneSelector.selectFormControl.reset();
    this.milestoneSelector.disable(message);
    this.resetBuildVersions("Please select milestone.");
  }

  updateMilestones(newMilestones: string[]) {
    this.milestones = newMilestones;
    if (this.milestones.length === 0) {
      this.milestoneSelector.disable(
        'No milestones found for the model.'
      );
    } else {
      this.milestoneSelector.enable();
    }
  }

  milestoneChanged(milestone: string): void {
    this.build.milestone = milestone;
    this.loadBuildVersions();
  }

  loadBuildVersions(): void {
    this.resetBuildVersions("loading...");
    this.loadingOverlay.updateStatus("Loading build versions ...", LoadingOverlayStyle.Top)
    this.moblabGrpcService.listBuildVersions(
      this.board,
      this.model,
      this.build.milestone,
      (buildVersions, _) => {
        this.updateBuildVersions(buildVersions);
        this.loadingOverlay.hide();
      },
      (errorMessage) => {this.showErrorMessage(errorMessage);}
    );
  }

  resetBuildVersions(mesage: string) {
    this.buildVersions = [];
    this.buildSelector.selectFormControl.reset();
    this.buildSelector.disable(mesage);
    this.canStart = false;
  }

  updateBuildVersions(newBuildVersions: string[]) {
    this.buildVersions = newBuildVersions;

    if (this.buildVersions.length === 0) {
      this.buildSelector.disable('No builds found for the milestone.');
    } else {
      this.buildSelector.enable();
    }
  }

  buildVersionChanged(buildVersion: string): void {
    this.build.buildVersion = buildVersion;
    this.canStart = true;
  }

  showErrorMessage(message: string) {
    this.loadingOverlay.updateStatus(message, LoadingOverlayStyle.Top)
  }
}
