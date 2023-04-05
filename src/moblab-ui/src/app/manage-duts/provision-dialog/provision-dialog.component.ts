import {AfterViewInit, Component, Inject, ViewChild} from '@angular/core';
import {MAT_DIALOG_DATA} from '@angular/material/dialog';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {
  LoadingOverlayComponent,
  LoadingOverlayStyle,
} from 'app/widgets/loading-overlay/loading-overlay.component';
import {ConnectedDutInfo} from 'app/services/moblabrpc_pb';
import {SelectableItem} from 'app/run-suite/common/basic-autocomplete-selector/basic-autocomplete-selector.component';

export interface DialogData {
  milestone: string;
  buildVersion: string;
  pool: string;
}

@Component({
  selector: 'app-provision-dialog',
  templateUrl: 'provision-dialog.component.html',
  styleUrls: ['provision-dialog.component.scss'],
})
export class ProvisionDialogComponent implements AfterViewInit {
  @ViewChild('buildSelector') buildSelector;
  @ViewChild('milestoneSelector') milestoneSelector;
  @ViewChild('poolSelector') poolSelector;
  @ViewChild(LoadingOverlayComponent) loadingOverlay: LoadingOverlayComponent;

  milestones: SelectableItem[] = [];
  buildVersions: SelectableItem[] = [];
  pools: SelectableItem[] = [];

  build: DialogData = {milestone: '', buildVersion: '', pool: ''};

  private model = '';
  private board = '';
  public canStart = false;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: {duts: ConnectedDutInfo[]},
    private moblabGrpcService: MoblabGrpcService
  ) {}

  ngAfterViewInit() {
    this.milestoneSelector.disable('Please select milestone.');
    this.buildSelector.disable('Please select build version.');
    this.loadPools();
  }

  loadPools(): void {
    const message = "Loading pools...";
    this.resetPools(message);
    this.loadingOverlay.updateStatus(
      message,
      LoadingOverlayStyle.Top
    );
    this.moblabGrpcService.listPools(
      pools => {
        pools.push('<all>');
        this.updatePools(pools);
        this.loadingOverlay.hide();
      },
      errorMessage => {
        this.showErrorMessage(errorMessage);
      },
      null,
    );
  }

  resetPools(message: string) {
    this.pools = [];
    this.poolSelector.disable(message);
    this.resetMilestones("Please select a pool.");
  }

  updatePools(pools: string[]) {
    this.pools = pools.map(p => new SelectableItem(p));
    this.poolSelector.enable();
  }

  poolChanged(pool: string): void {
    if (pool !== this.build.pool) {
      this.unselectMilestone();
      if (pool === '<all>') {
        pool = '';
      }
      this.build.pool = pool;
      const chosenDut = this.data.duts.find(
        d => !pool || d.getPoolsList()?.includes(pool)
      );
      this.model = chosenDut.getModel();
      this.board = chosenDut.getBuildTarget();
      this.loadMilestones();
    }
  }

  loadMilestones(): void {
    const message = "Loading milestones...";
    this.resetMilestones(message);
    this.loadingOverlay.updateStatus(
      message,
      LoadingOverlayStyle.Top
    );
    this.moblabGrpcService.listMilestones(
      this.board,
      this.model,
      (milestones, _) => {
        this.updateMilestones(milestones);
        this.loadingOverlay.hide();
      },
      errorMessage => {
        this.showErrorMessage(errorMessage);
      }
    );
  }

  resetMilestones(message: string) {
    this.milestones = [];
    this.milestoneSelector.disable(message);
    this.resetBuildVersions("Please select a milestone.");
  }

  updateMilestones(newMilestones: string[]) {
    this.milestones = newMilestones.map(m => new SelectableItem(m));

    if (this.milestones.length === 0) {
      this.milestoneSelector.disable('No milestones found for the model.');
    } else {
      this.milestoneSelector.enable();
    }
  }

  milestoneChanged(milestone: string): void {
    if (milestone !== this.build.milestone) {
      this.unselectBuildVersion();
      this.build.milestone = milestone;
      this.loadBuildVersions();
    }
  }

  loadBuildVersions(): void {
    const message = "Loading build version...";
    this.resetBuildVersions(message);
    this.loadingOverlay.updateStatus(
      message,
      LoadingOverlayStyle.Top
    );
    this.moblabGrpcService.listBuildVersions(
      this.board,
      this.model,
      this.build.milestone,
      '',
      '',
      (buildVersions: {version: string; status: string}[], _) => {
        this.updateBuildVersions(buildVersions);
        this.loadingOverlay.hide();
      },
      errorMessage => {
        this.showErrorMessage(errorMessage);
      }
    );
  }

  resetBuildVersions(message: string) {
    this.buildVersions = [];
    this.buildSelector.disable(message);
    this.canStart = false;
  }

  updateBuildVersions(
    newBuildVersions: {
      version: string;
      status: string;
    }[]
  ) {
    this.buildVersions = newBuildVersions.map(
      v => new SelectableItem(v.version, v.status)
    );

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
    this.loadingOverlay.updateStatus(message, LoadingOverlayStyle.Top);
  }

  unselectMilestone(): void {
    this.build.milestone = null;
    this.milestoneSelector.clearSelection();
    this.unselectBuildVersion();
    this.buildSelector.disable('Please select milestone.');
  }

  unselectBuildVersion(): void {
    this.build.buildVersion = null;
    this.buildSelector.clearSelection();
  }
}
