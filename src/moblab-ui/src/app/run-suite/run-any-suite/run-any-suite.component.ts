import {
  AfterContentInit,
  ChangeDetectorRef,
  Component,
  ViewChild,
} from '@angular/core';

import {MatSnackBar} from '@angular/material/snack-bar';
import {Router} from '@angular/router';

import {BaseSuite} from '../common/base_suite/base-suite.component';
import {MoblabGrpcService} from './../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../common/run-suite-button/run-suite-button.component';

/** Component owns logic for run-any-suite form. This component allows for the
 *  execution of any runnable suite, but without custom arguments.
 * */
@Component({
  selector: 'app-run-any-suite',
  templateUrl: './run-any-suite.component.html',
})
export class RunAnySuiteComponent
  extends BaseSuite
  implements AfterContentInit {
  @ViewChild('suiteInput') suiteInput;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

  MANUAL_SUITE_ENTRY_DESC = '>> Enter suite name';
  public suiteList: string[] = [
    this.MANUAL_SUITE_ENTRY_DESC,
    'au_fsi',
    'bvt-cq',
    'bvt-inline',
    'bvt-tast-cq',
    'usb-camera',
    'wifi_matfunc',
    'wifi_perf',
    'labqual',
  ];

  public hideCustomInput = true;

  public suiteName = '';

  constructor(
    private changeDetector: ChangeDetectorRef,
    moblabGrpcService: MoblabGrpcService,
    router: Router,
    snackBar: MatSnackBar
  ) {
    super(moblabGrpcService, router, snackBar);
  }

  /** Sets initial form enable/disable states.
   * */
  ngAfterContentInit(): void {
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

  /** Method triggered on change of suite input form.
   * */
  suiteDropdownChanged(suiteName: string) {
    if (suiteName != this.MANUAL_SUITE_ENTRY_DESC) {
      this.hideCustomInput = true;
      this.suiteName = suiteName;
      this.suiteInput.disable('Please select build.');
      this.runSuiteButton.enable();
    } else {
      this.hideCustomInput = false;
      this.suiteInput.enable();
      this.suiteName = null;
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

    if (!this.suiteName) {
      this.suiteName = this.suiteInput.getInput();
    }

    this.moblabGrpcService.runSuite(
      response => {
        this.onSuiteStarted();
      },
      (err, response) => {
        this.setOffPopup(err.message);
        this.runSuiteButton.enable();
      },
      this.suiteName,
      this.selectedBuild,
      this.selectedMilestone,
      this.selectedBoard,
      this.selectedModel,
      this.selectedPool
    );
  }
}
