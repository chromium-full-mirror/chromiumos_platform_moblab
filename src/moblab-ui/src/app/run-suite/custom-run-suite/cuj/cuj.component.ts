import {AfterContentInit, Component, ViewChild} from '@angular/core';

import {Router} from '@angular/router';

import {BaseSuite} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {BasicSelectorComponent} from '../../common/basic-selector/basic-selector.component';
import {NotificationsService} from 'app/services/notifications.service';
import {ConnectedDutInfo} from 'app/services/moblabrpc_pb';

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
    'performance_cuj',
    'performance_cuj_quick',
  ];

  public suiteName = '';
  public suiteLabel = '';
  public cujCheckError = '';
  public hideCustomInput = true;

  labelSelectDisabled = true;
  duts = new Array<ConnectedDutInfo>();
  dutHostnames = new Array<string>();

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
      this.getConnectedDuts();
      this.suiteSelectForm.disable('Please select build.');
      this.externalDisplayToggle.disable();
    });
  }

  /**
   * Fetches DUTs for use and label modification
   */
  getConnectedDuts() {
    this.moblabGrpcService.listConnectedDuts(
      (connectedDuts: ConnectedDutInfo[]) => {
        this.duts = connectedDuts;
        this.dutHostnames = connectedDuts.map(dut => dut.getIp());
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
  addLabel(dut_hostnames: string[], label: string) {
    this.moblabGrpcService.addLabelToDuts(
      message => {
        this.getConnectedDuts();
      },
      message => {
        this.cujCheckError = message;
      },
      dut_hostnames,
      label
    );
  }

  /**
   * Remove specified label from list of DUT IPs
   */
  removeLabel(dut_hostnames: string[], label) {
    this.moblabGrpcService.removeLabelFromDuts(
      message => {
        this.getConnectedDuts();
      },
      message => {
        this.cujCheckError = message;
      },
      dut_hostnames,
      label
    );
  }

  /** Method is triggered when build version form no longer has a valid
   * build version selected.
   * */
  onBuildVersionUnselected() {
    this.basicSelectorComponent.clearSelection();
    this.basicSelectorComponent.disable();
    this.runSuiteButton.disable();
  }

  /** Method triggered on change of custom suite input form.
   * */
  suiteChanged() {
    this.suiteName = this.suiteInput.getInput();
  }

  /** Method triggered on change of suite dropdown.
   * */
  suiteDropdownChanged(suiteName: string) {
    if (suiteName !== this.MANUAL_SUITE_ENTRY_DESC) {
      this.hideCustomInput = true;
      this.suiteInput.disable('Please select build.');
      this.suiteName = suiteName;
    } else {
      this.hideCustomInput = false;
      this.suiteInput.enable();
      this.suiteName = this.suiteInput.getInput();
    }
    this.labelSelectDisabled = false;
  }

  /** Method triggered on change of custom suite input form.
   * */
  suiteLabelChanged(suiteLabel: string) {
    this.suiteLabel = suiteLabel;
    this.externalDisplayToggle.enable();
    this.runSuiteButton.enable();
  }

  /** Method triggered on complete setting of build-related arguments.
   * ( model, build-target, milestone, build-version ).
   * */
  onBuildSetCustom(event) {
    this.suiteSelectForm.enable();
  }

  /**
   * Method to validate DUT label setting based on chosen suiteVersion.
   * If no suiteVersion is chosen, suite will be run using current labels.
   */
  handleDutSetup() {
    switch (this.suiteLabel) {
      case 'basic':
        this.removeLabel(this.dutHostnames, 'plus');
        this.removeLabel(this.dutHostnames, 'premium');
        break;
      case 'plus':
        this.addLabel(this.dutHostnames, 'plus');
        this.removeLabel(this.dutHostnames, 'premium');
        break;
      case 'premium':
        this.addLabel(this.dutHostnames, 'plus');
        this.addLabel(this.dutHostnames, 'premium');
        break;
    }
    if (this.externalDisplayToggle.getChecked()) {
      this.addLabel(this.dutHostnames, 'external_display');
    } else {
      this.removeLabel(this.dutHostnames, 'external_display');
    }
  }

  /** Method triggered on run-suite button press. Invokes runSuite RPC call.
   * */
  onRunSuiteClick() {
    super.onRunSuiteClick('Starting CUJ suite run.');
    this.handleDutSetup();

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
}
