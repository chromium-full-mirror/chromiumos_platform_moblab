import { Component, OnInit, ViewChild } from "@angular/core";

import { MoblabGrpcService } from "./../../../services/moblab-grpc.service";

interface CtsSuiteConfiguration {
  suiteLabel: string;
  suiteName: string;
}

interface CtsLetterConfiguration {
  label: string;
  config: CtsSuiteConfiguration[];
}

@Component({
  selector: "app-cts-run",
  templateUrl: "./cts-run.component.html",
  styleUrls: ["./cts-run.component.scss"]
})
export class CtsRunComponent {
  @ViewChild("runSuiteButton") runSuiteButton;
  @ViewChild("androidGroup") androidGroup;

  runSuiteButtonDisabled = true;
  selectedBuild: string;
  selectedBoard: string;
  selectedModel: string;
  selectedPool: string;
  selectedSuiteLabel: string;

  moduleCsvList: string = "";

  letterConfigs: CtsLetterConfiguration[] = [
    {
      label: "Android N",
      config: [
        { suiteLabel: "CTS", suiteName: "cts_N" },
        { suiteLabel: "GTS", suiteName: "gts" }
      ]
    },
    {
      label: "Android P",
      config: [
        { suiteLabel: "CTS", suiteName: "cts_P" },
        { suiteLabel: "GTS", suiteName: "gts" }
      ]
    }
  ];

  constructor(private moblabGrpcService: MoblabGrpcService) {}

  selectedIndex = 0;

  modelBoardPoolSelected(event) {
    if (event.build) {
      console.log(event.build);
      this.selectedBuild = event.build;
    }
    if (event.board) {
      this.selectedBoard = event.board;
    }
    if (event.model) {
      console.log(event.model);
      this.selectedModel = event.model;
    }
    if (event.pool) {
      console.log(event.pool);
      this.selectedPool = event.pool;
    }
  }

  getSuiteLabelList(androidConfig: CtsLetterConfiguration) {
    var labels: string[] = [];
    androidConfig.config.forEach(config => {
      labels.push(config.suiteLabel);
    });
    return labels;
  }

  getSuiteNameFromLabel(androidConfig: CtsLetterConfiguration, label: string) {
    let config: CtsSuiteConfiguration = androidConfig.config.find(
      config => config.suiteLabel == label
    );
    if (config) {
      return config.suiteName;
    } else {
      console.log("Fatal Error, can not find %s in %s", label, androidConfig);
    }
  }

  suiteChanged(selectedSuite: string) {
    this.selectedSuiteLabel = selectedSuite;
    this.runSuiteButtonDisabled = false;
  }

  onRunSuite() {
    let suite = this.getSuiteNameFromLabel(
      this.letterConfigs[this.selectedIndex],
      this.selectedSuiteLabel
    );
    this.moblabGrpcService.runCtsSuite(
      this.selectedBuild,
      this.selectedBoard,
      this.selectedModel,
      suite,
      this.selectedPool,
      this.moduleCsvList,
      ""
    );
  }
}
