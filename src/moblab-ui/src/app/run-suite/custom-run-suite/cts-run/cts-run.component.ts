import {Component, OnInit, ViewChild} from '@angular/core';

import {MoblabGrpcService} from './../../../services/moblab-grpc.service';

@Component({
  selector: 'app-cts-run',
  templateUrl: './cts-run.component.html',
  styleUrls: ['./cts-run.component.scss']
})
export class CtsRunComponent {
  @ViewChild('runSuiteButton') runSuiteButton;
  @ViewChild('androidGroup') androidGroup;

  runSuiteButtonDisabled = true;
  selectedBuild: string;
  selectedModel: string;
  selectedPool: string;
  selectedSuiteLabel: string;
  selectedSuiteIndex = 0;

  androidConfigurations = [
    {
      label: 'Android N',
      suites:
          [
            {label: 'CTS', suiteName: 'cts_N'},
            {label: 'GTS', suiteName: 'gts'}
          ]
    },
    {
      label: 'Android P',
      suites:
          [
            {label: 'CTS', suiteName: 'cts_P'},
            {label: 'GTS', suiteName: 'gts'}
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
    if (event.model) {
      console.log(event.model);
      this.selectedModel = event.model;
    }
    if (event.pool) {
      console.log(event.pool);
      this.selectedPool = event.pool;
    }
  }

  getSuiteLabel(suiteLabelNameMap) {
    return suiteLabelNameMap.label;
  }

  getSuiteName(suiteLabelNameMap, suiteLabel) {
    return suiteLabelNameMap.label;
  }

  getSuiteLabelList(androidConfig) {
    return androidConfig.suites.map(this.getSuiteLabel);
  }

  suiteChanged(selectedSuite: string) {
    this.selectedSuiteLabel = selectedSuite;
    this.runSuiteButtonDisabled = false;
  }

  onRunSuite() {
    var suite = this.androidConfigurations[this.selectedIndex]['suites'][this.selectedSuiteIndex]['suiteName'];

    this.moblabGrpcService.runCtsSuite(
        this.selectedBuild, 'board', this.selectedModel,
        suite, '', '', '');
  }
}
