import { Component, OnInit, ViewChild } from '@angular/core';

import {BaseSuite} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from './../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {BasicTextFormComponent} from '../../common/basic-text-form/basic-text-form.component';
import {Router} from '@angular/router';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-gts-run',
  templateUrl: './gts-run.component.html',
})
export class GtsRunComponent extends BaseSuite implements OnInit {
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;
  @ViewChild(BasicTextFormComponent) modulesTextForm;

  constructor(moblabGrpcService: MoblabGrpcService,
              router: Router,
              snackBar: MatSnackBar) {
    super(moblabGrpcService, router, snackBar);
  }

  ngOnInit(): void {
    this.modulesTextForm.disable('Please select build.');
  }

  onBuildSetCustom(event) {
    this.modulesTextForm.enable();
    this.runSuiteButton.enable();
  }

  onRunSuite() {
    this.moblabGrpcService.runGtsSuite(
      (response) => {
        this.redirectToViewJobs();
      },
      (err, response) => {
        this.setOffPopup(response.getMessage());
      },
      this.selectedBuild,
      this.selectedMilestone,
      this.selectedBoard,
      this.selectedModel,
      this.selectedPool,
      this.modulesTextForm.getText(),
    );
  }
}
