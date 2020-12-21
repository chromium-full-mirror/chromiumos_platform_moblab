import {
  AfterContentInit,
  ChangeDetectorRef,
  Component,
  ViewChild
} from '@angular/core';

import {BaseSuite} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from './../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {Router} from '@angular/router';
import {MatSnackBar} from '@angular/material/snack-bar';
import {RunStorageQualificationSuiteRequest} from '../../../services/moblabrpc_pb';

@Component({
  selector: 'app-storage-qual-v2',
  templateUrl: './storage-qual-v2.component.html',
  styleUrls: ['./storage-qual-v2.component.scss']
})
export class StorageQualV2Component extends BaseSuite implements AfterContentInit {
  @ViewChild('bugIdInput') bugIdInput;
  @ViewChild('partNumberInput') partNumberInput;
  @ViewChild('diskSizeInput') diskSizeInput;
  @ViewChild('suiteSelector') suiteSelector;
  @ViewChild('dualNamespace') dualNamespace;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

  readonly suiteOptions = [
    'Quick test',
    'Extra short test (2 testing blocks)',
    'Short test (10 testing blocks)',
    'Medium test (20 testing blocks)',
    'Long test (30 testing blocks)',
    'Extra long test (40 testing blocks)'
  ]
  suiteIndex = 0; // Index of currently seleted suite.

  constructor(private changeDetector: ChangeDetectorRef,
    moblabGrpcService: MoblabGrpcService,
    router: Router,
    snackBar: MatSnackBar) {
    super(moblabGrpcService, router, snackBar);
  }

  /** Sets initial form enable/disable states.
   * */
  ngAfterContentInit(): void {
    this.disableTestParamControls();
    this.bugIdInput.disable('Please select disk size.');
    this.partNumberInput.disable('Please select disk size.');
    this.changeDetector.detectChanges();
  }

  onBuildSetCustom(event) {
    this.diskSizeInput.enable();
    this.suiteSelector.enable();
    this.dualNamespace.enable();
  }

  diskInputChanged() {
    if (this.diskSizeInput.getInput()) {
      if (this.diskSizeInput.getInput() < 35) {
        this.suiteSelector.selectOption(1)
      } else if (this.diskSizeInput.getInput() < 70) {
        this.suiteSelector.selectOption(2)
      } else if (this.diskSizeInput.getInput() < 140) {
        this.suiteSelector.selectOption(3)
      } else if (this.diskSizeInput.getInput() < 280) {
        this.suiteSelector.selectOption(4)
      } else {
        this.suiteSelector.selectOption(5)
      }
      this.bugIdInput.enable();
      this.partNumberInput.enable();
    }
  }

  /** Method triggered on change of either bug ID or part number.
   * */
  avlInputChanged() {
    if (this.bugIdInput.getInput() && this.partNumberInput.getInput()) {
      this.runSuiteButton.enable();
    } else {
      this.runSuiteButton.disable();
    }
  }

  /** Method triggered on change of variation selector
   * */
  suiteChanged(newSuite) {
    this.suiteIndex = newSuite ? this.suiteOptions.indexOf(newSuite) : 0;
  }

  /** Method is triggered when build version form no longer has a valid
   * build version selected.
   * */
  onBuildVersionUnselected() {
    this.disableTestParamControls();
    this.runSuiteButton.disable();
  }

  disableTestParamControls() {
    this.diskSizeInput.disable('Please select build.');
    this.suiteSelector.disable('Please select build.');
    this.dualNamespace.disable('Please select build.');
  }

  /** Method triggered on run-suite button press. Invokes
   *  runStorageQualificationSuite RPC call.
   * */
  onRunSuiteClick() {
    super.onRunSuiteClick('Starting storage qualification suite run.');

    this.moblabGrpcService.runStorageQualificationSuite(
      (response) => {
        this.onSuiteStarted();
      },
      (err, response) => {
        this.onRunSuiteFailed(err.message);
        this.runSuiteButton.enable();
      },
      this.selectedBuild,
      this.selectedMilestone,
      this.selectedBoard,
      this.selectedModel,
      this.selectedPool,
      this.bugIdInput.getInput(),
      this.partNumberInput.getInput(),
      this.suiteIndex + Number(RunStorageQualificationSuiteRequest.Variation.QUICK_V2),
      this.diskSizeInput.getInput(),
      this.dualNamespace.getChecked()
    );
  }
}
