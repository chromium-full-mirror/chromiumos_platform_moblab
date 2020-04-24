import {Component, EventEmitter, Input, Output, ViewChild, OnInit} from '@angular/core';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {BuildSettings} from '../base_suite/base-suite.component';


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
export class BuildSelectFormsComponent implements OnInit {
  @ViewChild('modelSelector') modelSelector;
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

  constructor(private moblabGrpcService: MoblabGrpcService) {}

  ngOnInit() {
    this.modelSelector.disable('Models not loaded.');
    this.boardSelector.disable('Please select model.');
    this.buildSelector.disable('Please select build target.');
    this.poolSelector.disable('Please select build.');

    this.moblabGrpcService.listModels((boards: string[]) => {
      this.updateModels(boards);
    });
  }

  updateModels(newModels: string[]) {
    this.modelSelector.enable();
    this.models = newModels;
  }

  modelChanged(model: string) {
    this.selectedModel = model;
    this.boardSelector.enable();
    this.moblabGrpcService.listBuildTargets((buildTarget: string[]) => {
      this.updateBuildTargets(buildTarget);
    });
  }

  updateBuildTargets(newBuildTargets: string[]) {
    this.buildTargets = newBuildTargets;
  }

  buildTargetChanged(newBuildTarget: string): void {
    this.buildTargetName = newBuildTarget;
    this.buildSelector.enable();
    this.moblabGrpcService.listBuildVersions(
      this.buildTargetName, this.milestone, (builds: string[]) => {
        this.updateBuildVersions(builds);
      });
  }

  updateBuildVersions(newBuildVersions: string[]) {
    this.buildVersions = newBuildVersions;
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
      this.moblabGrpcService.listPools((pools: string[]) => {
        this.updatePools(pools);
      });
    }
  }

  updatePools(newPools: string[]) {
    this.pools = newPools;
  }

  poolChanged(pool: string) {
    this.selectedPool = pool;
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
      pool: this.pools
    })
  }
}
