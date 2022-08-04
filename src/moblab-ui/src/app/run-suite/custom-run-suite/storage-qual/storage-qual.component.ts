import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  ViewChild,
} from '@angular/core';

import {BaseSuite} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from './../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {Router} from '@angular/router';
import {RunStorageQualificationSuiteRequest} from '../../../services/moblabrpc_pb';
import {NotificationsService} from 'app/services/notifications.service';

@Component({
  selector: 'app-storage-qual',
  templateUrl: './storage-qual.component.html',
  styleUrls: ['./storage-qual.component.scss'],
})
export class StorageQualComponent extends BaseSuite implements AfterViewInit {
  @ViewChild('bugIdInput') bugIdInput;
  @ViewChild('partNumberInput') partNumberInput;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

  readonly variationOptions = [''].concat(
    Object.keys(RunStorageQualificationSuiteRequest.Variation).slice(1, 3)
  );
  variationSelection = 0;

  isStorageQualSetupValid = false;
  storageQualCheckError = '';

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
    this.bugIdInput.disable('Please select build.');
    this.partNumberInput.disable('Please select build.');
    this.changeDetector.detectChanges();
  }

  onBuildSetCustom(event) {
    this.bugIdInput.enable();
    this.partNumberInput.enable();
  }

  /** Method triggered on change of either bug ID or part number.
   * */
  inputChanged() {
    if (
      this.bugIdInput.getInput() &&
      this.partNumberInput.getInput() &&
      this.isStorageQualSetupValid
    ) {
      this.runSuiteButton.enable();
    } else {
      this.runSuiteButton.disable();
    }
  }

  /** Method triggered on change of variation selector
   * */
  variationChanged(newVariation) {
    this.variationSelection = newVariation
      ? Number(RunStorageQualificationSuiteRequest.Variation[newVariation])
      : 0;
    this.validateStorageQualSetup();
  }

  /** Method is triggered when build version form no longer has a valid
   * build version selected.
   * */
  onBuildVersionUnselected() {
    this.runSuiteButton.disable();
  }

  /** Method triggered on run-suite button press. Invokes
   *  runStorageQualificationSuite RPC call.
   * */
  onRunSuiteClick() {
    super.onRunSuiteClick('Starting storage qualification suite run.');

    this.moblabGrpcService.runStorageQualificationSuite(
      response => {
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
      this.variationSelection,
      0, // Disk size in GB.
      false, // Test dual namespace devices.
      false // this feature is not available in v1 version of storage_qual
    );
  }

  validateStorageQualSetup() {
    this.storageQualCheckError = '';
    this.isStorageQualSetupValid = false;
    this.inputChanged();

    const variationsToCheck = [
      RunStorageQualificationSuiteRequest.Variation.VARIATION_NOT_SET,
      RunStorageQualificationSuiteRequest.Variation.QUICK,
    ];
    if (!variationsToCheck.includes(this.variationSelection)) {
      this.isStorageQualSetupValid = true;
      this.inputChanged();
      return;
    }
    this.onFormLoading('validating storage qual setup ...');
    this.moblabGrpcService.validateStorageQualSetup(
      () => {
        this.isStorageQualSetupValid = true;
        this.storageQualCheckError = '';
        this.inputChanged();
        this.onFormLoaded();
      },
      (msg: string) => {
        this.storageQualCheckError = msg;
        this.inputChanged();
        this.onFormLoaded();
      },
      this.selectedModel,
      this.selectedBoard,
      this.selectedPool,
    );
  }
}
