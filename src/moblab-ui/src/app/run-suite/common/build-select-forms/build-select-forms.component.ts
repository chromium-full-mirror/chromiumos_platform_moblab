import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';

import {BuildSettings} from '../base_suite/base-suite.component';
import {MatSnackBar} from '@angular/material/snack-bar';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';


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
  styleUrls: ['./build-select-forms.component.css']
})
export class BuildSelectFormsComponent implements OnInit, AfterViewInit {
  @ViewChild('modelSelector') modelSelector;
  @ViewChild('milestoneSelector') milestoneSelector;
  @ViewChild('boardSelector') boardSelector;
  @ViewChild('buildSelector') buildSelector;
  @ViewChild('poolSelector') poolSelector;

  @Output() formLoading = new EventEmitter();
  @Output() formLoaded = new EventEmitter();
  @Output() allRequiredFieldsSet = new EventEmitter();

  // TODO(haddowk) Allow tryjobs and other build types.
  buildType = 'release';
  buildTargets: string[] = [];
  milestones: string[] = [];
  buildVersions: string[] = [];
  models: string[] = [];
  pools: string[] = [];

  private selectedModel: string;
  private selectedBuild: string;
  private selectedPool: string;
  private buildTargetName = '';
  private milestone = '';
  private buildVersionName = '';

  constructor(
    private changeDetector: ChangeDetectorRef,
    private moblabGrpcService: MoblabGrpcService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit() {
    this.getModels();
  }

  ngAfterViewInit() {
    this.boardSelector.disable(SELECT_MODEL_PROMPT);
    this.milestoneSelector.disable(SELECT_BUILD_TARGET_PROMPT);
    this.buildSelector.disable(SELECT_MILESTONE_PROMPT);
    this.poolSelector.disable(SELECT_BUILD_VERSION_PROMPT);
    this.changeDetector.detectChanges();
  }

  setOffError(dialogue: string) {
    const snackBarRef = this.snackBar.open(dialogue, 'Dismiss', {
      verticalPosition: 'top',
      panelClass: ['snack-error']
    });
  }

  setErrorReason(selector, msg: string) {
    msg = 'Failed to fetch items: ' + msg;
    selector.disable(msg);
    this.setOffError(msg);
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
    this.models = newModels;

    if (newModels.length === 0) {
      this.modelSelector.disable('No working DUT\'s detected.');
    } else {
      this.modelSelector.enable();
    }
  }

  modelChanged(model: string) {
    this.selectedModel = model;
    this.getBuildTargets();
  }

  getBuildTargets() {
    this.formLoading.emit({message:'fetching build targets...'});
    this.moblabGrpcService.listBuildTargets(
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
    this.buildTargets = newBuildTargets;

    if (this.buildTargets.length === 0) {
      this.boardSelector.disable('No build targets found in configured bucket.');
    } else {
      this.boardSelector.enable();
    }
  }

  buildTargetChanged(newBuildTarget: string): void {
    this.buildTargetName = newBuildTarget;
    this.getMilestones();
  }

  getMilestones() {
    this.formLoading.emit({message:'fetching milestones...'});
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
    )
  }

  updateMilestones(newMilestones: string[]) {
    this.milestones = newMilestones;

    if (this.milestones.length === 0) {
      this.milestoneSelector.disable('No milestones found in configured bucket.');
    } else {
      this.milestoneSelector.enable();
    }
  }

  milestoneChanged(newMilestone: string): void {
    this.milestone = newMilestone;
    this.getBuildVersions();
  }

  getBuildVersions() {
    this.formLoading.emit({message:'fetching build versions...'});
    this.moblabGrpcService.listBuildVersions(
      this.buildTargetName,
      this.selectedModel,
      this.milestone,
      (builds: string[]) => {
        this.updateBuildVersions(builds);
        this.formLoaded.emit();
      },
      (error_msg: string) => {
        this.setErrorReason(this.buildSelector, error_msg);
        this.formLoaded.emit();
      }
    );
  }

  updateBuildVersions(newBuildVersions: string[]) {
    this.buildVersions = newBuildVersions;

    if (this.buildVersions.length === 0) {
      this.buildSelector.disable('No builds found in configured bucket.');
    } else {
      this.buildSelector.enable();
    }
  }

  buildVersionChanged(newBuildVersion: string): void {
    this.buildVersionName = newBuildVersion;
    this.poolSelector.enable();
    this.buildChanged(this.getBuildFormattedString(), this.buildTargetName);
    this.emitBuildSelections();
  }

  buildChanged(build: string, board: string) {
    if (build) {
      this.selectedBuild = build;
      this.moblabGrpcService.listPools(
        (pools: string[]) => {
          this.updatePools(pools);
        },
        (error_msg: string) => {
          this.setErrorReason(this.poolSelector, error_msg);
        });
    }
  }

  updatePools(newPools: string[]) {
    this.pools = [''].concat(newPools);
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
      pool: this.selectedPool
    })
  }

  unselectModel() {
    this.selectedModel = null;
    this.boardSelector.clearSelection();
    this.boardSelector.disable(SELECT_MODEL_PROMPT);
    this.unselectBuildTarget();
  }

  unselectBuildTarget() {
    this.buildTargetName = null;
    this.milestoneSelector.clearSelection();
    this.milestoneSelector.disable(SELECT_BUILD_TARGET_PROMPT);
    this.unselectMilestone();
  }

  unselectMilestone() {
    this.milestone = null;
    this.buildSelector.clearSelection();
    this.buildSelector.disable(SELECT_MILESTONE_PROMPT);
    this.unselectBuildVersion();
  }

  unselectBuildVersion() {
    this.buildVersionName = null;
    this.poolSelector.disable(SELECT_BUILD_VERSION_PROMPT);
  }
}
