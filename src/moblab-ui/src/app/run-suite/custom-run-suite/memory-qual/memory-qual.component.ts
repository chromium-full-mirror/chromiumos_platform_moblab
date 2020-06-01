import { Component, OnInit, ViewChild } from '@angular/core';

import {BaseSuite} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from './../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {BasicTextFormComponent} from '../../common/basic-text-form/basic-text-form.component';
import {Router} from '@angular/router';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-memory-qual',
  templateUrl: './memory-qual.component.html',
  styleUrls: ['./memory-qual.component.scss']
})
export class MemoryQualComponent extends BaseSuite implements OnInit {
  @ViewChild('bugIdInput') bugIdInput;
  @ViewChild('partNumberInput') partNumberInput;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

  constructor(moblabGrpcService: MoblabGrpcService,
              router: Router,
              snackBar: MatSnackBar) {
    super(moblabGrpcService, router, snackBar);
  }

  ngOnInit(): void {
    this.bugIdInput.disable('Please select build.');
    this.partNumberInput.disable('Please select build.');
  }

  onBuildSetCustom(event) {
    this.bugIdInput.enable();
    this.partNumberInput.enable();
  }

  avlInputChanged(event) {
    if (this.bugIdInput.getInput() && this.partNumberInput.getInput()) {
      this.runSuiteButton.enable();
    } else {
      this.runSuiteButton.disable();
    }
  }

  onRunSuite() {
    this.moblabGrpcService.runStorageQualificationSuite(
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
      this.bugIdInput.getInput(),
      this.partNumberInput.getInput()
    );
  }
}
