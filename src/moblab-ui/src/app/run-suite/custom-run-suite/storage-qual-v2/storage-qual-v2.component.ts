import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  ViewChild,
} from '@angular/core';

import {
  BaseSuite,
  BuildSettings,
} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from './../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {Router} from '@angular/router';
import {RunStorageQualificationSuiteRequest} from '../../../services/moblabrpc_pb';
import {NotificationsService} from 'app/services/notifications.service';

@Component({
  selector: 'app-storage-qual-v2',
  templateUrl: './storage-qual-v2.component.html',
  styleUrls: ['./storage-qual-v2.component.scss'],
})
export class StorageQualV2Component extends BaseSuite implements AfterViewInit {
  @ViewChild('bugIdInput') bugIdInput;
  @ViewChild('partNumberInput') partNumberInput;
  @ViewChild('diskSizeInput') diskSizeInput;
  @ViewChild('suiteSelector') suiteSelector;
  @ViewChild('dualNamespace') dualNamespace;
  @ViewChild('isPreQualified') isPreQualified;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

  readonly suiteOptions = [
    'Quick test',
    'Extra short test (2 testing blocks)',
    'Short test (10 testing blocks)',
    'Medium test (20 testing blocks)',
    'Long test (30 testing blocks)',
    'Extra long test (40 testing blocks)',
  ];
  suiteIndex = 0; // Index of currently seleted suite.

  isStorageQualSetupValid: boolean = false;
  storageQualCheckError: string = '';

  constructor(
    private changeDetector: ChangeDetectorRef,
    moblabGrpcService: MoblabGrpcService,
    router: Router,
    notificationsService: NotificationsService
  ) {
    super(moblabGrpcService, router, notificationsService);
  }

  /** Sets initial form enable/disable states.
   * */
  ngAfterViewInit(): void {
    this.disableTestParamControls();
    this.bugIdInput.disable('Please select disk size.');
    this.partNumberInput.disable('Please select disk size.');
    this.changeDetector.detectChanges();
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  onBuildSetCustom() {
    this.diskSizeInput.enable();
    this.suiteSelector.enable();
    this.dualNamespace.enable();
    this.isPreQualified.enable();
  }

  diskInputChanged() {
    if (this.diskSizeInput.getInput()) {
      this.suiteSelector.selectOption(5);
      this.bugIdInput.enable();
      this.partNumberInput.enable();
    }
  }

  /** Method triggered on change of either bug ID or part number.
   * */
  avlInputChanged() {
    if (this.bugIdInput.getInput() && this.partNumberInput.getInput() && this.isStorageQualSetupValid) {
      this.runSuiteButton.enable();
    } else {
      this.runSuiteButton.disable();
    }
  }

  /** Method triggered on change of variation selector
   * */
  suiteChanged(newSuite: string) {
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
    this.isPreQualified.disable('Please select build.');
  }

  /** Method triggered on run-suite button press. Invokes
   *  runStorageQualificationSuite RPC call.
   * */
  onRunSuiteClick() {
    super.onRunSuiteClick('Starting storage qualification suite run.');

    this.moblabGrpcService.runStorageQualificationSuite(
      _response => {
        this.onSuiteStarted();
      },
      (err, _response) => {
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
      this.suiteIndex +
        Number(RunStorageQualificationSuiteRequest.Variation.QUICK_V2),
      this.diskSizeInput.getInput(),
      this.dualNamespace.getChecked(),
      this.isPreQualified.getChecked()
    );
  }

  validateStorageQualSetup() {
    this.storageQualCheckError = '';
    this.isStorageQualSetupValid = false;
    this.avlInputChanged();

    const variationsToCheck = [
      RunStorageQualificationSuiteRequest.Variation.QUICK_V2,
      RunStorageQualificationSuiteRequest.Variation.XS,
      RunStorageQualificationSuiteRequest.Variation.S,
      RunStorageQualificationSuiteRequest.Variation.M,
      RunStorageQualificationSuiteRequest.Variation.L,
      RunStorageQualificationSuiteRequest.Variation.XL,
    ];
    const variation = this.suiteIndex + Number(RunStorageQualificationSuiteRequest.Variation.QUICK_V2);

    if (!variationsToCheck.includes(variation)) {
      this.isStorageQualSetupValid = true;
      return;
    }

    this.onFormLoading('validating storage qual setup ...');
    this.moblabGrpcService.validateStorageQualSetup(
      () => {
        this.isStorageQualSetupValid = true;
        this.storageQualCheckError = '';
       this.avlInputChanged();
        this.onFormLoaded();
      },
      (msg: string) => {
        this.storageQualCheckError = msg;
        this.avlInputChanged();
        this.onFormLoaded();
      },
      this.selectedModel,
      this.selectedBoard,
      this.selectedPool,
    );
  }
}
