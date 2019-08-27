import {
  Component,
  Input,
  Output,
  EventEmitter,
  ViewChild
} from "@angular/core";
import { MoblabGrpcService } from "app/services/moblab-grpc.service";

@Component({
  selector: "app-moblab-build-selector",
  templateUrl: "./moblab-build-selector.component.html",
  styleUrls: ["./moblab-build-selector.component.scss"]
})
export class MoblabBuildSelectorComponent {
  constructor(private moblabGrpcService: MoblabGrpcService) {}

  @ViewChild("boardSelector") boardSelector;
  @ViewChild("milestoneSelector") milestoneSelector;
  @ViewChild("buildSelector") buildSelector;

  @Output() update = new EventEmitter();

  boards: string[] = [];
  boardsPickerActive = false;
  milestones: string[] = [];
  milestonesPickerActive = false;
  builds: string[] = [];
  buildsPickerActive = false;

  private boardName = "";
  private milestone = "";
  private buildName = "";
  // TODO(haddowk) Allow tryjobs and other build types.
  buildType = "release";

  start(): void {
    this.moblabGrpcService.listBoards((boards: string[]) => {
      this.updateBoards(boards);
    });
  }

  updateBoards(newBoards: string[]) {
    this.boards = newBoards;
    this.boardsPickerActive = true;
  }

  boardChanged(boardName, selectedIndex): void {
    this.boardName = boardName;
    this.moblabGrpcService.listMilestones(boardName, (milestones: string[]) => {
      this.updateMilestones(milestones);
    });
  }

  updateMilestones(newMilestones: string[]) {
    this.milestones = newMilestones;
    this.milestonesPickerActive = true;
  }

  milestoneChanged(milestone, selectedIndex): void {
    console.log(milestone);
    this.milestone = milestone;
    this.moblabGrpcService.listBuilds(
      this.boardName,
      milestone,
      (builds: string[]) => {
        this.builds = builds;
      }
    );
  }

  updateBuilds(newBuilds: string[]) {
    this.builds = newBuilds;
    this.buildsPickerActive = true;
  }

  buildChanged(buildName, selectedIndex): void {
    this.buildName = buildName;
    this.update.emit({ value: this.getBuildFormattedString() });
  }

  getBuildFormattedString(): string {
    return `${this.boardName}-${this.buildType}/${this.milestone}-${
      this.buildName
    }`;
  }
}
