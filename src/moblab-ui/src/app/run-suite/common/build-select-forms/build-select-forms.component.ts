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
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {MatSnackBar} from '@angular/material/snack-bar';


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
    this.moblabGrpcService.listModels(
      (models: string[]) => {
        this.updateModels(models);
      },
      (error_msg: string) => {
        this.setErrorReason(this.modelSelector, error_msg);
      });
  }

  ngAfterViewInit() {
    this.boardSelector.disable('Please select model.');
    this.milestoneSelector.disable('Please select build target.');
    this.buildSelector.disable('Please select milestone.');
    this.poolSelector.disable('Please select build.');
    this.changeDetector.detectChanges();
  }

  setOffPopup(dialogue: string) {
    const snackBarRef = this.snackBar.open(dialogue, '', {
      duration: 5000,
      verticalPosition: 'top'
    });
  }

  setErrorReason(selector, msg: string) {
    msg = 'Failed to fetch items: ' + msg;
    selector.disable(msg);
    this.setOffPopup(msg);
  }

  updateModels(newModels: string[]) {
    this.models = newModels;

    if (this.models.length === 0) {
      this.modelSelector.disable('No working DUT\'s detected.');
    } else {
      this.modelSelector.enable();
    }
  }

  modelChanged(model: string) {
    this.selectedModel = model;
    this.moblabGrpcService.listBuildTargets(
      (buildTarget: string[]) => {
        this.updateBuildTargets(buildTarget);
      },
      (error_msg: string) => {
        this.setErrorReason(this.boardSelector, error_msg);
      });
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
    this.moblabGrpcService.listMilestones(this.buildTargetName,
      (milestones: string[]) => {
        this.updateMilestones(milestones);
      },
      (error_msg: string) => {
        this.setErrorReason(this.milestoneSelector, error_msg);
      },
    )
  }

  updateMilestones(newMilestones: string[]) {
    this.milestones = newMilestones;

    if (this.buildTargets.length === 0) {
      this.milestoneSelector.disable('No milestones found in configured bucket.');
    } else {
      this.milestoneSelector.enable();
    }
  }

  milestoneChanged(newMilestone: string): void {
    this.milestone = newMilestone;
    this.moblabGrpcService.listBuildVersions(
      this.buildTargetName, this.milestone,
      (builds: string[]) => {
        this.updateBuildVersions(builds);
      },
      (error_msg: string) => {
        this.setErrorReason(this.buildSelector, error_msg);
      }
    );
  }

  updateBuildVersions(newBuildVersions: string[]) {
    this.buildVersions = newBuildVersions;

    if (this.buildTargets.length === 0) {
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
}
