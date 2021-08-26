import {Component, ViewChild} from '@angular/core';
import {
  LoadingOverlayComponent,
  LoadingOverlayStyle,
} from 'app/widgets/loading-overlay/loading-overlay.component';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {BuildSelectFormsComponent} from 'app/run-suite/common/build-select-forms/build-select-forms.component';

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
export class StageBuildDialogComponent {
  @ViewChild(LoadingOverlayComponent) loadingOverlay: LoadingOverlayComponent;
  @ViewChild(BuildSelectFormsComponent)
  buildSelectForm: BuildSelectFormsComponent;

  stageBuildNotification: StageBuildNotification;
  stageBuildButtonDisabled = true;
  buildBucketUrl: string;
  returnMessage: string;

  selectedBuild = '';
  selectedBuildTarget = '';
  selectedMilestone = '';
  selectedModel = '';

  constructor(public moblabGrpcService: MoblabGrpcService) {}

  onBuildSet(event) {
    this.selectedModel = event.model;
    this.selectedBuildTarget = event.board;
    this.selectedMilestone = event.milestone;
    this.selectedBuild = event.build;
    this.stageBuildButtonDisabled = false;
  }

  onBuildVersionUnselected() {
    this.stageBuildButtonDisabled = true;
  }

  async stageBuild() {
    const buildId = this._formatBuildId();
    this.updateLoadingOverlay('Staging the test build...');
    this.disableAllSelectors();
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
      this.enableAllSelectors();
      this.stageBuildNotification = new StageBuildNotification(
        STAGE_BUILD_ERROR_MESSAGE,
        StageBuildStatus.ERROR,
        ERROR_ICON,
        'error'
      );
    }
    this.hideLoadingOverlay();
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
    this.buildSelectForm.modelSelector.enable();
    this.buildSelectForm.boardSelector.enable();
    this.buildSelectForm.milestoneSelector.enable();
    this.buildSelectForm.buildSelector.enable();
  }

  disableAllSelectors() {
    this.stageBuildButtonDisabled = true;
    this.buildSelectForm.modelSelector.disable();
    this.buildSelectForm.boardSelector.disable();
    this.buildSelectForm.milestoneSelector.disable();
    this.buildSelectForm.buildSelector.disable();
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
}
