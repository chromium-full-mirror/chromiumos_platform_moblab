import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  EventEmitter,
  Input,
  Output,
  ViewChild,
} from '@angular/core';

import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {SelectableItem} from '../basic-autocomplete-selector/basic-autocomplete-selector.component';
import {NotificationsService} from 'app/services/notifications.service';
const SELECT_MODEL_PROMPT = 'Please select model.';
const SELECT_BUILD_TARGET_PROMPT = 'Please select build target.';
const SELECT_MILESTONE_PROMPT = 'Please select milestone.';
const SELECT_BUILD_VERSION_PROMPT = 'Please select build.';

/**
 * Component packages form items for selecting model, board, build, and pool.
 * These are always set in custom suite forms, and therefore packaged together
 * for ease of repeated use.
 */
@Component({
  selector: 'app-build-select-forms',
  templateUrl: './build-select-forms.component.html',
  styleUrls: ['./build-select-forms.component.css'],
})
export class BuildSelectFormsComponent implements AfterViewInit {
  @ViewChild('modelSelector') modelSelector;
  @ViewChild('milestoneSelector') milestoneSelector;
  @ViewChild('boardSelector') boardSelector;
  @ViewChild('buildSelector') buildSelector;
  @ViewChild('poolSelector') poolSelector;
  @ViewChild('buildDisplayToggle') buildDisplayToggle;

  @Input() hidePoolSelector?: boolean = false;
  @Input() recommendedBuildLabel?: string = '';
  @Output() formLoading = new EventEmitter();
  @Output() formLoaded = new EventEmitter();
  @Output() allRequiredFieldsSet = new EventEmitter();
  @Output() buildVersionUnselected = new EventEmitter();

  // TODO(haddowk) Allow tryjobs and other build types.
  buildType = 'release';
  buildTargets: SelectableItem[] = [];
  milestones: SelectableItem[] = [];
  buildVersions: SelectableItem[] = [];
  models: SelectableItem[] = [];
  pools: SelectableItem[] = [];

  private selectedModel: string;
  private selectedBuild: string;
  private selectedPool: string;
  private buildTargetName = '';
  private milestone = '';
  private buildVersionName = '';
  private disabledReasonMessage = '';
  public showRecommendedBuilds = this.recommendedBuildLabel;

  constructor(
    private changeDetector: ChangeDetectorRef,
    public moblabGrpcService: MoblabGrpcService,
    private notificationsService: NotificationsService
  ) {}

  ngAfterViewInit() {
    this.getModels();

    this.boardSelector.disable(SELECT_MODEL_PROMPT);
    this.milestoneSelector.disable(SELECT_BUILD_TARGET_PROMPT);
    this.buildSelector.disable(SELECT_MILESTONE_PROMPT);
    if (!this.hidePoolSelector) {
      this.poolSelector.disable(SELECT_BUILD_VERSION_PROMPT);
    }
    this.changeDetector.detectChanges();
  }

  setErrorReason(selector, msg: string) {
    msg = 'Failed to fetch items: ' + msg;
    selector.disable(msg);
    this.notificationsService.error(msg);
  }

  getModels() {
    this.formLoading.emit({message: 'fetching models...'});
    this.moblabGrpcService.listModels(
      (models: string[]) => {
        this.updateModels(models);
        this.formLoaded.emit();
      },
      (error_msg: string) => {
        this.setErrorReason(this.modelSelector, error_msg);
        this.formLoaded.emit();
      }
    );
  }

  updateModels(newModels: string[]) {
    this.models = newModels.map(m => new SelectableItem(m));

    if (newModels.length === 0) {
      this.modelSelector.disable("No working DUT's detected.");
    } else {
      this.modelSelector.enable();
    }
  }

  modelChanged(model: string) {
    if (this.selectedModel !== model) {
      this.unselectBuildTarget();
      this.selectedModel = model;
      this.getBuildTargets();
    }
  }

  getBuildTargets() {
    this.formLoading.emit({message: 'fetching build targets...'});
    this.moblabGrpcService.listBuildTargetsByModel(
      this.selectedModel,
      (buildTargets: string[]) => {
        this.updateBuildTargets(buildTargets);
        this.formLoaded.emit();
      },
      (error_msg: string) => {
        this.setErrorReason(this.boardSelector, error_msg);
        this.formLoaded.emit();
      }
    );
  }

  updateBuildTargets(newBuildTargets: string[]) {
    this.buildTargets = newBuildTargets.map(bt => new SelectableItem(bt));

    if (this.buildTargets.length === 0) {
      this.boardSelector.disable(
        'No build targets found in configured bucket.'
      );
    } else {
      this.boardSelector.enable();
    }
  }

  buildTargetChanged(newBuildTarget: string): void {
    if (this.buildTargetName !== newBuildTarget) {
      this.unselectMilestone();
      this.buildTargetName = newBuildTarget;
      this.getMilestones();
    }
  }

  getMilestones() {
    this.formLoading.emit({message: 'fetching milestones...'});
    this.moblabGrpcService.listMilestones(
      this.buildTargetName,
      this.selectedModel,
      (milestones: string[]) => {
        this.updateMilestones(milestones);
        this.formLoaded.emit();
      },
      (error_msg: string) => {
        this.setErrorReason(this.milestoneSelector, error_msg);
        this.formLoaded.emit();
      }
    );
  }

  updateMilestones(newMilestones: string[]) {
    this.milestones = newMilestones.map(m => new SelectableItem(m));

    if (this.milestones.length === 0) {
      this.milestoneSelector.disable(
        'No milestones found in configured bucket.'
      );
    } else {
      this.milestoneSelector.enable();
    }
  }

  milestoneChanged(newMilestone: string): void {
    if (this.milestone !== newMilestone) {
      this.milestone = newMilestone;
      if(this.buildDisplayToggle) {
        this.enableBuildToggle();
      } else {
        this.unselectBuildVersion();
        this.getBuildVersions();
      }
    }
  }

  buildDisplayChanged() {
    this.unselectBuildVersion();
    this.showRecommendedBuilds = this.buildDisplayToggle.checked ? this.recommendedBuildLabel : '';
    this.getBuildVersions();
  }

  getBuildVersions() {
    if (this.showRecommendedBuilds !== '') {
      this.formLoading.emit({message: 'fetching recommended build versions...'});
    } else {
      this.formLoading.emit({message: 'fetching build versions...'});
    }
    this.moblabGrpcService.listBuildVersions(
      this.buildTargetName,
      this.selectedModel,
      this.milestone,
      this.showRecommendedBuilds,
      this.recommendedBuildLabel,
      (builds: {version: string; status: string}[]) => {
        this.updateBuildVersions(builds);
        this.formLoaded.emit();
      },
      (error_msg: string) => {
        this.setErrorReason(this.buildSelector, error_msg);
        this.formLoaded.emit();
      }
    );
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
      this.buildSelector.disable('No builds found in configured bucket.');
    } else {
      this.buildSelector.enable();
    }
    if (this.buildVersions.length === 0 && this.buildDisplayToggle.checked) {
      this.disableBuildToggle();
    }
  }

  buildVersionChanged(newBuildVersion: string): void {
    this.buildVersionName = newBuildVersion;
    if (!this.hidePoolSelector) {
      this.poolSelector.enable();
    }
    this.buildChanged(this.getBuildFormattedString(), this.selectedModel);
    this.emitBuildSelections();
  }

  buildChanged(build: string, model: string) {
    if (build) {
      this.selectedBuild = build;
      if (this.hidePoolSelector) {
        return;
      }
      this.moblabGrpcService.listPools(
        (pools: string[]) => {
          this.updatePools(pools);
        },
        (error_msg: string) => {
          this.setErrorReason(this.poolSelector, error_msg);
        },
	model,
      );
    }
  }

  updatePools(newPools: string[]) {
    this.pools = [''].concat(newPools).map(pool => new SelectableItem(pool));
  }

  poolChanged(pool: string) {
    this.selectedPool = pool;
    this.emitBuildSelections();
  }

  getBuildFormattedString(): string {
    return this.buildVersionName;
  }

  emitBuildSelections() {
    this.allRequiredFieldsSet.emit({
      build: this.getBuildFormattedString(),
      board: this.buildTargetName,
      model: this.selectedModel,
      milestone: this.milestone,
      buildVersionName: this.buildVersionName,
      pool: this.selectedPool,
    });
  }

  unselectModel() {
    this.selectedModel = null;
    this.unselectBuildTarget();
    this.boardSelector.disable(SELECT_MODEL_PROMPT);
  }

  unselectBuildTarget() {
    this.buildTargetName = null;
    this.boardSelector.clearSelection();
    this.unselectMilestone();
    this.milestoneSelector.disable(SELECT_BUILD_TARGET_PROMPT);
  }

  unselectMilestone() {
    this.milestone = null;
    this.milestoneSelector.clearSelection();
    this.unselectBuildVersion();
    this.buildSelector.disable(SELECT_MILESTONE_PROMPT);
    if(this.buildDisplayToggle) {
      this.buildDisplayToggle.disabled = true
    }
  }

  unselectBuildVersion() {
    this.buildVersionName = null;
    this.buildSelector.clearSelection();
    if (!this.hidePoolSelector) {
      this.poolSelector.disable(SELECT_BUILD_VERSION_PROMPT);
    }
    this.buildVersionUnselected.emit();
  }

  enableBuildToggle() {
    this.buildDisplayToggle.disabled = false;
    this.disabledReasonMessage = '';
    this.buildDisplayChanged();
  }

  disableBuildToggle() {
    this.buildDisplayToggle.disabled = true;
    this.buildDisplayToggle.checked = false;
    this.disabledReasonMessage = 'No recommended builds for this milestone';
    this.buildDisplayChanged();
  }

  getDisabledReason() {
    return this.disabledReasonMessage;
  }
}
