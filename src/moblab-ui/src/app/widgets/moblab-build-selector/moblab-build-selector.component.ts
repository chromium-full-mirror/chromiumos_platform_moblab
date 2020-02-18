import {Component, EventEmitter, Input, Output, ViewChild} from '@angular/core';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';

@Component({
  selector: 'app-moblab-build-selector',
  templateUrl: './moblab-build-selector.component.html',
  styleUrls: ['./moblab-build-selector.component.scss']
})
export class MoblabBuildSelectorComponent {
  @ViewChild('boardSelector', { static: true }) boardSelector;
  @ViewChild('milestoneSelector', { static: true }) milestoneSelector;
  @ViewChild('buildSelector', { static: true }) buildSelector;

  @Output() update = new EventEmitter();

  buildTargets: string[] = [];
  buildTargetsPickerActive = false;
  milestones: string[] = [];
  milestonesPickerActive = false;
  buildVersions: string[] = [];
  buildVersionsPickerActive = false;

  private buildTargetName = '';
  private milestone = '';
  private buildVersionName = '';
  // TODO(haddowk) Allow tryjobs and other build types.
  buildType = 'release';
  constructor(private moblabGrpcService: MoblabGrpcService) {}

  start(): void {
    this.moblabGrpcService.listBuildTargets((buildTarget: string[]) => {
      this.updateBuildTargets(buildTarget);
    });
  }

  updateBuildTargets(newBuildTargets: string[]) {
    this.buildTargets = newBuildTargets;
    this.buildTargetsPickerActive = true;
  }

  buildTargetChanged(newBuildTarget): void {
    this.buildTargetName = newBuildTarget;
    this.moblabGrpcService.listMilestones(this.buildTargetName, (milestones: string[]) => {
      this.updateMilestones(milestones);
    });
    this.update.emit({board: this.buildTargetName});
  }

  updateMilestones(newMilestones: string[]) {
    this.milestones = newMilestones;
    this.milestonesPickerActive = true;
  }

  milestoneChanged(newMilestone): void {
    this.milestone = newMilestone;
    this.moblabGrpcService.listBuildVersions(
        this.buildTargetName, this.milestone, (builds: string[]) => {
          this.buildVersions = builds;
        });
  }

  updateBuildVersions(newBuildVersions: string[]) {
    this.buildVersions = newBuildVersions;
    this.buildVersionsPickerActive = true;
  }

  buildVersionChanged(newBuildVersion): void {
    this.buildVersionName = newBuildVersion;
    this.update.emit({build: this.getBuildFormattedString()});
  }

  getBuildFormattedString(): string {
    return `${this.buildTargetName}-${this.buildType}/${this.milestone}-${
        this.buildVersionName}`;
  }
}
