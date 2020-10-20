import {AfterViewInit, ChangeDetectorRef, Component, ViewChild} from '@angular/core';

import {MatSnackBar} from '@angular/material/snack-bar';
import {Router} from '@angular/router';

import {BaseSuite} from '../common/base_suite/base-suite.component';
import {BasicTextFormComponent} from '../common/basic-text-form/basic-text-form.component';
import {MoblabGrpcService} from './../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../common/run-suite-button/run-suite-button.component';


/** Component owns logic for run-any-suite form. This component allows for the
 *  execution of any runnable suite, but without custom arguments.
 * */
@Component({
  selector: 'app-run-any-suite',
  templateUrl: './run-any-suite.component.html',
})
export class RunAnySuiteComponent extends BaseSuite implements AfterViewInit {
  @ViewChild('suiteInput') suiteInput;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

  constructor(
    private changeDetector: ChangeDetectorRef,
    moblabGrpcService: MoblabGrpcService,
    router: Router,
    snackBar: MatSnackBar) {
    super(moblabGrpcService, router, snackBar);
  }

  /** Sets initial form enable/disable states.
   * */
  ngAfterViewInit(): void {
    this.suiteInput.disable('Please select build.');
    this.changeDetector.detectChanges();
  }

  /** Method triggered on change of suite input form.
   * */
  suiteChanged() {
    if (this.suiteInput.getInput()) {
      this.runSuiteButton.enable();
    } else {
      this.runSuiteButton.disable();
    }
  }

  /** Method triggered on complete setting of build-related arguments.
   * ( model, build-target, milestone, build-version ).
   * */
  onBuildSetCustom(event) {
    this.suiteInput.enable();
  }

  /** Method is triggered when build version form no longer has a valid
   * build version selected.
   * */
  onBuildVersionUnselected() {
    this.runSuiteButton.disable();
  }

  /** Method triggered on run-suite button press. Invokes runSuite RPC call.
   * */
  onRunSuiteClick() {
    super.onRunSuiteClick('Starting suite run.');

    this.moblabGrpcService.runSuite(
      (response) => {
        this.onSuiteStarted();
      },
      (err, response) => {
        this.setOffPopup(err.message);
        this.runSuiteButton.enable();
      },
      this.suiteInput.getInput(),
      this.selectedBuild,
      this.selectedMilestone,
      this.selectedBoard,
      this.selectedModel,
      this.selectedPool,
    );
  }
}
