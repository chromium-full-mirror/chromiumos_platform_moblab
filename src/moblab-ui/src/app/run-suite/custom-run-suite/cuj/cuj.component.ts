import { AfterContentInit, Component, ViewChild } from '@angular/core';

import { Router } from '@angular/router';

import { BaseSuite } from '../../common/base_suite/base-suite.component';
import { MoblabGrpcService } from 'app/services/moblab-grpc.service';
import { RunSuiteButtonComponent } from '../../common/run-suite-button/run-suite-button.component';
import { BasicSelectorComponent } from '../../common/basic-selector/basic-selector.component';
import { NotificationsService } from 'app/services/notifications.service';
import { ConnectedDutInfo } from 'app/services/moblabrpc_pb';

const BASIC = 'basic';
const PLUS = 'plus';
const PREMIUM = 'premium';
const ESSENTIAL = 'essential';
const ADVANCED = 'advanced';

/** Component owns logic for CUJ suite run form.
 * */
@Component({
  selector: 'app-cuj',
  templateUrl: './cuj.component.html',
  styleUrls: ['./cuj.component.scss'],
})
export class CUJRunComponent extends BaseSuite implements AfterContentInit {
  @ViewChild('suiteInput') suiteInput;
  @ViewChild('suiteSelector') suiteSelectForm;
  @ViewChild('labelSelector') labelSelectForm;
  @ViewChild('externalDisplayToggle') externalDisplayToggle;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;
  @ViewChild(BasicSelectorComponent) basicSelectorComponent;

  MANUAL_SUITE_ENTRY_DESC = '>> Enter suite name';
  readonly suiteList: string[] = [
    this.MANUAL_SUITE_ENTRY_DESC,
    'performance_cuj_v2',
    'performance_cuj_quick_v2',
    'performance_cuj',
    'performance_cuj_quick',
  ];

  public suiteName = '';
  public suiteLabel = BASIC;
  public cujCheckError = '';
  public hideCustomInput = true;
  public recommendedBuildTag = 'Spera:GoodBuild';
  options: [string, string][] = [];
  options_v1: [string, string][] = [
    [BASIC, 'Basic'],
    [PLUS, 'Plus'],
    [PREMIUM, 'Premium'],
  ];
  options_v2: [string, string][] = [
    [ESSENTIAL, 'Essential'],
    [ADVANCED, 'Advanced'],
  ];
  errorMessage: string | null = null;

  labelSelectDisabled = false;
  duts = new Array<ConnectedDutInfo>();
  dutHostnames = new Array<string>();

  private buildSelected = false;

  constructor(
    moblabGrpcService: MoblabGrpcService,
    router: Router,
    notificationsService: NotificationsService
  ) {
    super(moblabGrpcService, router, notificationsService);
  }

  /** Sets initial form enable/disable states.
   * */
  ngAfterContentInit(): void {
    setTimeout(() => {
      this.getConnectedDuts(() => { });
      // These two enable can make the tooptips `This form is disable` disappear.
      this.suiteSelectForm.enable();
    });
  }

  /**
   * Fetches DUTs for use and label modification
   */
  getConnectedDuts(callback: () => void) {
    this.moblabGrpcService.listConnectedDuts(
      (connectedDuts: ConnectedDutInfo[]) => {
        this.duts = connectedDuts;
        callback();
      },
      (message: string) => {
        this.duts = [];
        this.cujCheckError = message;
      }
    );
  }

  /**
   * Add specified label to list of DUT IPs
   */
  addLabel(label: string, callback: () => void) {
    this.moblabGrpcService.addLabelToDuts(
      message => {
        this.getConnectedDuts(callback);
      },
      message => {
        this.cujCheckError = message;
      },
      this.dutHostnames,
      label
    );
  }

  /**
   * Remove specified label from list of DUT IPs
   */
  removeLabel(label, callback: () => void) {
    this.moblabGrpcService.removeLabelFromDuts(
      message => {
        this.getConnectedDuts(callback);
      },
      message => {
        this.cujCheckError = message;
      },
      this.dutHostnames,
      label
    );
  }

  /** Method is triggered when build version form no longer has a valid
   * build version selected.
   * */
  onBuildVersionUnselected() {
    this.buildSelected = false;
    this._isReadyToRun();
  }

  /** Method triggered on change of custom suite input form.
   * */
  suiteChanged() {
    this.suiteName = this.suiteInput.getInput().trim();
    this._isReadyToRun();
  }

  /** Method triggered on change of suite dropdown.
   * */
  suiteDropdownChanged(suiteName: string) {
    if (suiteName !== this.MANUAL_SUITE_ENTRY_DESC) {
      this.hideCustomInput = true;
      this.suiteInput.disable('Please select build.');
      this.suiteName = suiteName;
      this.updateLabelList();
    } else {
      this.hideCustomInput = false;
      this.suiteInput.enable();
      this.suiteName = this.suiteInput.getInput();
      this.options = [];
    }
    this._isReadyToRun();
  }

  /** Method to update display of label options
   * */
  updateLabelList() {
    if (this.suiteName.includes('_v2')) {
      this.options = this.options_v2;
      this.externalDisplayToggle.disable();
    } else {
      this.options = this.options_v1;
      this.externalDisplayToggle.enable();
    }
  }

  /** Method triggered on change of custom suite input form.
   * */
  suiteLabelChanged(suiteLabel: string) {
    this.suiteLabel = suiteLabel;
    this._isReadyToRun();
  }

  /** Method triggered on complete setting of build-related arguments.
   * ( model, build-target, milestone, build-version ).
   * */
  onBuildSetCustom(event) {
    this.buildSelected = true;
    this._isReadyToRun();
  }

  /**
   * Method to validate DUT label setting based on chosen suiteVersion.
   * If no suiteVersion is chosen, suite will be run using current labels.
   */
  handleDutSetupAndTriggerRunSuiute() {
    this.dutHostnames = this.getSelectedDutHostnames(this.duts);
    switch (this.suiteLabel) {
      case BASIC:
        // First remove plus label, then remove premium label and last
        // trigger the actual suite
        this.removeLabel('plus', () => {
          this.removeLabel('premium', () => {
            this.triggerRunSuite();
          });
        });
        break;
      case PLUS:
        this.addLabel('plus', () => {
          this.removeLabel('premium', () => {
            this.triggerRunSuite();
          });
        });
        break;
      case PREMIUM:
        this.addLabel('plus', () => {
          this.addLabel('premium', () => {
            this.triggerRunSuite();
          });
        });
        break;
      case ESSENTIAL:
        this.addLabel('essential', () => {
          this.removeLabel('advanced', () => {
            this.triggerRunSuite();
          });
        });
        break;
      case ADVANCED:
        this.addLabel('advanced', () => {
          this.removeLabel('essential', () => {
            this.triggerRunSuite();
          });
        });
        break;
    }
  }

  private _isReadyToRun() {
    if (this.buildSelected && this._validate()) {
      this.runSuiteButton.enable();
    } else {
      this.runSuiteButton.disable();
    }
  }

  private _validate(): boolean {
    this.reset();
    if (!this.suiteLabel) {
      this.errorMessage = 'Please select the suite label.';
      return false;
    }
    if (!this.suiteName) {
      this.errorMessage = this.hideCustomInput
        ? ''
        : 'Please input a suite name.';
      return false;
    }

    return true;
  }

  reset(): void {
    this.errorMessage = null;
  }

  triggerRunSuite() {
    this.moblabGrpcService.runSuite(
      _ => {
        this.onSuiteStarted();
      },
      (err, _) => {
        this.onRunSuiteFailed(err.message);
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
  /** Method triggered on run-suite button press. Invokes runSuite RPC call.
   * */
  onRunSuiteClick() {
    super.onRunSuiteClick('Starting CUJ suite run.');
    if (!this._validate()) {
      this.onFormLoaded();
      return;
    }
    // this needs to be handled differently as suite is triggered already
    if (this.externalDisplayToggle.getChecked()) {
      this.addLabel('external_display', () => {
        this.handleDutSetupAndTriggerRunSuiute();
      });
    } else {
      this.removeLabel('external_display', () => {
        this.handleDutSetupAndTriggerRunSuiute();
      });
    }
  }
}
