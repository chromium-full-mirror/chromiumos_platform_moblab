import {AfterViewInit, Component, ViewChild} from '@angular/core';
import {
  LoadingOverlayComponent,
  LoadingOverlayStyle,
} from 'app/widgets/loading-overlay/loading-overlay.component';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {Model} from 'app/services/moblabrpc_pb';
import {SelectableItem} from 'app/run-suite/common/basic-autocomplete-selector/basic-autocomplete-selector.component';
import {build_access_request_link} from '../../constants';

export interface BuildVersion {
  version: string;
  status: string;
}

export enum StageBuildStatus {
  SUCCESS,
  ERROR,
}

const STAGE_BUILD_SUCCESS_MESSAGE = 'Successfully staged the test build.';
const STAGE_BUILD_ERROR_MESSAGE =
  'Failed to stage the test build, please try again.';
const SUCCESS_ICON = 'check_circle';
const ERROR_ICON = 'error';

export class StageBuildNotification {
  constructor(
    public message: string,
    public status: StageBuildStatus,
    public icon: string,
    public cssClass: string
  ) {}
}
const GCS_URL = 'https://console.developers.google.com/storage/';

@Component({
  selector: 'app-stage-build-dialog',
  templateUrl: 'stage-build-dialog.component.html',
  styleUrls: ['stage-build-dialog.component.scss'],
})
export class StageBuildDialogComponent implements AfterViewInit {
  @ViewChild('modelSelector') modelSelector;
  @ViewChild('buildTargetSelector') buildTargetSelector;
  @ViewChild('milestoneSelector') milestoneSelector;
  @ViewChild('buildSelector') buildSelector;
  @ViewChild(LoadingOverlayComponent) loadingOverlay: LoadingOverlayComponent;

  models: SelectableItem[] = [];
  buildTargets: SelectableItem[] = [];
  milestones: SelectableItem[] = [];
  buildVersions: SelectableItem[] = [];
  accessibleModels: Model[] = [];
  stageBuildNotification: StageBuildNotification;
  stageBuildButtonDisabled = true;
  buildBucketUrl: string;
  returnMessage: string;

  selectedBuild = '';
  selectedBuildTarget = '';
  selectedMilestone = '';
  selectedModel = '';

  readonly build_access_request_link = build_access_request_link;

  constructor(public moblabGrpcService: MoblabGrpcService) {}

  ngAfterViewInit() {
    this.disableAllSelectors("Loading...");
    this.loadModels();
  }

  async listAccessibleModels() {
    try {
      this.accessibleModels = await this.moblabGrpcService.listAccessibleModelsPromise(
        '*'
      );
    } catch (error) {
      console.error(error);
    }
  }

  async loadModels() {
    const message = "Loading models...";
    this.resetModels(message);
    this.updateLoadingOverlay(message);
    await this.listAccessibleModels();
    this.hideLoadingOverlay();
    this.updateModels();
  }

  resetModels(message: string) {
    this.models = [];
    this.modelSelector.disable(message);
    this.resetBuildTarget("Please select a model.");
  }

  updateModels() {
    const models = this.accessibleModels.map(model => model.getName()).sort();
    this.models = models.map(m => new SelectableItem(m));
    if (this.models.length === 0) {
      this.modelSelector.disable(
        'No model found, please refresh and try again.'
      );
    } else {
      this.modelSelector.enable();
    }
  }

  modelChanged(model: string): void {
    if (model !== this.selectedModel) {
      this.stageBuildButtonDisabled = true;
      this.stageBuildNotification = null;
      this.unselectBuildTarget();
      this.selectedModel = model;
      this.loadBuildTargets();
    }
  }

  loadBuildTargets(): void {
    this.resetBuildTarget("Loading build targets...");
    const buioldTargets = this.accessibleModels
      .filter(e => e.getName() === this.selectedModel)[0]
      .getBuildTargetsList();
    this.buildTargets = buioldTargets.map(b => new SelectableItem(b));
    if (this.buildTargets.length === 0) {
      this.buildTargetSelector.disable('No build target found for this model.');
    } else {
      this.buildTargetSelector.enable();
    }
  }

  resetBuildTarget(message: string) {
    this.buildTargets = [];
    this.buildTargetSelector.disable(message);
    this.resetMilestones("Please select a build target.");
  }

  buildTargetChanged(buildTarget: string): void {
    if (buildTarget !== this.selectedBuildTarget) {
      this.stageBuildButtonDisabled = true;
      this.stageBuildNotification = null;
      this.unselectMilestone();
      this.selectedBuildTarget = buildTarget;
      this.loadMilestones();
    }
  }

  loadMilestones(): void {
    const message = "Loading milestones...";
    this.resetMilestones(message);
    this.updateLoadingOverlay(message);
    this.moblabGrpcService.listMilestones(
      this.selectedBuildTarget,
      this.selectedModel,
      (milestones: string[]) => {
        this.updateMilestones(milestones);
        this.hideLoadingOverlay();
      },
      (errorMessage: string) => {
        this.updateLoadingOverlay(errorMessage);
      }
    );
  }

  resetMilestones(message: string) {
    this.milestones = [];
    this.milestoneSelector.disable(message);
    this.resetBuildVersions("Please select a milestone.");
  }

  updateMilestones(milestones: string[]) {
    this.milestones = milestones.map(m => new SelectableItem(m));
    if (this.milestones.length === 0) {
      this.milestoneSelector.disable(
        'No milestones found for the selected model and build target.'
      );
    } else {
      this.milestoneSelector.enable();
    }
  }

  milestoneChanged(milestone: string): void {
    if (milestone !== this.selectedMilestone) {
      this.stageBuildButtonDisabled = true;
      this.stageBuildNotification = null;
      this.unselectBuildVersion();
      this.selectedMilestone = milestone;
      this.loadBuildVersions();
    }
  }

  loadBuildVersions(): void {
    const message = "Loading build versions..."
    this.resetBuildVersions(message);
    this.updateLoadingOverlay(message);
    this.moblabGrpcService.listBuildVersions(
      this.selectedBuildTarget,
      this.selectedModel,
      this.selectedMilestone,
      '',
      '',
      (buildVersions: BuildVersion[]) => {
        this.updateBuildVersions(buildVersions);
        this.hideLoadingOverlay();
      },
      (errorMessage: string) => {
        this.updateLoadingOverlay(errorMessage);
      }
    );
  }

  resetBuildVersions(message: string) {
    this.buildVersions = [];
    this.buildSelector.disable(message);
  }

  updateBuildVersions(buildVersions: BuildVersion[]) {
    this.buildVersions = buildVersions.map(
      v => new SelectableItem(v.version, v.status)
    );

    if (this.buildVersions.length === 0) {
      this.buildSelector.disable('No builds found for the milestone.');
    } else {
      this.buildSelector.enable();
    }
  }

  buildVersionChanged(buildVersion: string): void {
    this.selectedBuild = buildVersion;
    this.stageBuildNotification = null;
    this.stageBuildButtonDisabled = false;
  }

  async stageBuild() {
    const buildId = this._formatBuildId();
    this.updateLoadingOverlay('Staging the test build...');
    this.disableAllSelectors('Waiting for the stage build.');
    try {
      const buildBucket = await this.moblabGrpcService.stageBuildPromise(
        this.selectedModel,
        this.selectedBuildTarget,
        this.selectedBuild
      );
      this.stageBuildNotification = new StageBuildNotification(
        STAGE_BUILD_SUCCESS_MESSAGE,
        StageBuildStatus.SUCCESS,
        SUCCESS_ICON,
        'success'
      );
      this.buildBucketUrl = this._formatBuildBucketUrl(buildBucket);
      this.returnMessage = `Successfully staged the test build ${buildId} to gcs bucket: ${buildBucket}`;
    } catch (error) {
      this.stageBuildNotification = new StageBuildNotification(
        STAGE_BUILD_ERROR_MESSAGE,
        StageBuildStatus.ERROR,
        ERROR_ICON,
        'error'
      );
    }
    this.hideLoadingOverlay();
    this.enableAllSelectors();
  }

  hideLoadingOverlay() {
    this.loadingOverlay.hide();
  }

  updateLoadingOverlay(message: string) {
    this.loadingOverlay.show();
    this.loadingOverlay.updateStatus(message, LoadingOverlayStyle.Top);
  }

  enableAllSelectors() {
    this.stageBuildButtonDisabled = false;
    this.modelSelector.enable();
    this.buildTargetSelector.enable();
    this.milestoneSelector.enable();
    this.buildSelector.enable();
  }

  disableAllSelectors(message: string) {
    this.stageBuildButtonDisabled = true;
    this.modelSelector.disable(message);
    this.buildTargetSelector.disable(message);
    this.milestoneSelector.disable(message);
    this.buildSelector.disable(message);
  }

  isStageBuildSucceeded(): boolean {
    if (
      !this.stageBuildNotification ||
      this.stageBuildNotification.status === StageBuildStatus.ERROR
    ) {
      return false;
    }
    return true;
  }

  _formatBuildBucketUrl(buildBucket: string): string {
    const buildId = this._formatBuildId();
    return (
      GCS_URL + `${buildBucket}/${this.selectedBuildTarget}-release/${buildId}`
    );
  }

  _formatBuildId(): string {
    return `R${this.selectedMilestone}-${this.selectedBuild}`;
  }

  unselectModel(): void {
    this.selectedModel = null;
    this.unselectBuildTarget();
    this.buildTargetSelector.disable("Please select a model.");
  }

  unselectBuildTarget(): void {
    this.selectedBuildTarget = null;
    this.buildTargetSelector.clearSelection();
    this.unselectMilestone();
    this.milestoneSelector.disable("Please select a build target.");
  }

  unselectMilestone(): void {
    this.selectedMilestone = null;
    this.milestoneSelector.clearSelection();
    this.unselectBuildVersion();
    this.buildSelector.disable("Please select a milestone.");
  }

  unselectBuildVersion(): void {
    this.selectedBuild = null;
    this.buildSelector.clearSelection();
  }
}
