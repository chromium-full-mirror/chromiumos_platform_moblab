import {Component, OnInit, ViewChild} from '@angular/core';

import {MatSnackBar} from '@angular/material/snack-bar';
import {Router} from '@angular/router';

import {BaseSuite} from '../common/base_suite/base-suite.component';
import {BasicTextFormComponent} from '../common/basic-text-form/basic-text-form.component';
import {MoblabGrpcService} from './../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../common/run-suite-button/run-suite-button.component';

@Component({
  selector: 'app-run-any-suite',
  templateUrl: './run-any-suite.component.html',
})
export class RunAnySuiteComponent extends BaseSuite implements OnInit {
  @ViewChild('suiteInput') suiteInput;
  @ViewChild(BasicTextFormComponent) suiteNameForm;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

  constructor(moblabGrpcService: MoblabGrpcService,
    router: Router,
    snackBar: MatSnackBar) {
    super(moblabGrpcService, router, snackBar);
  }

  ngOnInit(): void {
    this.suiteInput.disable('Please select build.');
  }

  suiteChanged(event) {
    this.runSuiteButton.enable();
  }

  onBuildSetCustom(event) {
    this.suiteInput.enable();
  }

  onRunSuite() {
    this.moblabGrpcService.runSuite(
      (response) => {
        this.redirectToViewJobs();
      },
      (err, response) => {
        this.setOffPopup(err.message);
      },
      this.suiteInput.getInput(),
      this.selectedBuild,
      this.selectedBoard,
      this.selectedModel,
      this.selectedPool,
    );
  }
}
