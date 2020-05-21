import { Component, OnInit, ViewChild } from '@angular/core';

import {BaseSuite} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from './../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {BasicTextFormComponent} from '../../common/basic-text-form/basic-text-form.component';
import {Router} from '@angular/router';
import {MatSnackBar} from '@angular/material/snack-bar';

import {BuildSettings} from '../../common/base_suite/base-suite.component';

@Component({
  selector: 'app-cts-run',
  templateUrl: './cts-run.component.html',
})
export class CtsRunComponent extends BaseSuite implements OnInit {
  @ViewChild('versionSelector') versionSelectForm;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;
  @ViewChild(BasicTextFormComponent) modulesTextForm;

  selectedAndroidVersion: string;

  constructor(moblabGrpcService: MoblabGrpcService,
              router: Router,
              snackBar: MatSnackBar) {
    super(moblabGrpcService, router, snackBar);
  }

  ngOnInit(): void {
    this.versionSelectForm.disable('Please select build.');
    this.modulesTextForm.disable('Please select build.');
  }

  androidVersionChanged(selectedAndroidVersion: string) {
    this.selectedAndroidVersion = selectedAndroidVersion;
    this.runSuiteButton.enable();
  }

  onBuildSetCustom(event: BuildSettings) {
    this.modulesTextForm.enable();
    this.versionSelectForm.enable();
  }

  onRunSuite() {
    this.moblabGrpcService.runCtsSuite(
      (response) => {
        this.redirectToViewJobs();
      },
      (err, response) => {
        this.setOffPopup(response.getMessage());
      },
      this.selectedAndroidVersion,
      this.selectedBuild,
      this.selectedBoard,
      this.selectedModel,
      this.selectedPool,
      this.modulesTextForm.getText(),
    );
  }
}
