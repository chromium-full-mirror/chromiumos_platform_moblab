import {
  AfterContentInit, 
  AfterViewInit, 
  ChangeDetectorRef, 
  Component, 
  ViewChild
} from '@angular/core';

import {Router} from '@angular/router';
import {MatTableDataSource} from '@angular/material/table';
import {MatSelectChange} from "@angular/material/select";

import {BaseSuite} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from '../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {BasicSelectorComponent} from '../../common/basic-selector/basic-selector.component';
import {NotificationsService} from '../../../services/notifications.service';
import {BuildTargetAccessService} from '../../../services/build-target-access.service';
import {ConnectedDutInfo, GetPeripheralInformationResponse} from '../../../services/moblabrpc_pb';
import {SelectableItem} from "../../common/basic-autocomplete-selector/basic-autocomplete-selector.component";

interface keyable {
  [key: string]: any
}

/** Component owns logic for fwupd form. This component allows for the
 *  execution of any runnable suite, but without custom arguments.
 * */
@Component({
  selector: 'app-fwupd',
  templateUrl: './fwupd.component.html',
  styleUrls: ['./fwupd.component.scss'],
})
export class FWUPDRunComponent extends BaseSuite implements AfterViewInit {
  @ViewChild('suiteSelector') suiteSelectForm;
  @ViewChild('dutSelector') dutSelectForm;
  @ViewChild('deviceIdSelector') deviceIdSelector;
  @ViewChild('deviceInput') deviceInput;
  @ViewChild('certificateIdInput') certificateIdInput;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

  readonly FWUPD_UPDATE = 'fwupd_update';
  readonly FWUPD_DOWNGRADE = 'fwupd_downgrade';
  readonly FWUPD_INSTALL_VERSION = 'fwupd_install_version';
  readonly FWUPD_INSTALL_FILE = 'fwupd_install_file';

  public peripherals_info_json: JSON;
  public test_args: string[] = [];
  public dutIPs: string[] = [];
  public suiteList: string[] = [
      this.FWUPD_UPDATE,
      this.FWUPD_DOWNGRADE,
      this.FWUPD_INSTALL_VERSION,
      this.FWUPD_INSTALL_FILE
  ];

  public suiteName = '';
  public suiteSelected = false;
  private buildSelected = false;

  public cert_id: string | null = null;

  public dut_IP = '';

  public data: SelectableItem[] = [];
  public device_id: string | null = null;
  public device: keyable | null = null;
  public device_file_or_version: string | null = null;
  public peripheral_error: boolean = false;

  constructor(
    private changeDetector: ChangeDetectorRef,
    moblabGrpcService: MoblabGrpcService,
    router: Router,
    notificationsService: NotificationsService,
    private buildTargetAccessService: BuildTargetAccessService
  ) {
    super(moblabGrpcService, router, notificationsService);
  }

  /** Sets initial form enable/disable states.
   * */
  ngAfterViewInit(): void {
    this.changeDetector.detectChanges();
    this.suiteSelectForm.disable('Please select DUT');
    this.dutSelectForm.disable('Please select build');
  }

  getConnectedDuts() {
    this.onFormLoading("fetching DUT IPs...");
    this.moblabGrpcService.listConnectedDuts(
      (connectedDuts: ConnectedDutInfo[]) => {
	this.dutIPs = this.getSelectedDutHostnames(connectedDuts);
	this.onFormLoaded();
      },
      (message: string) => {
	this.dutIPs = [];
        this.onRunSuiteFailed(message);
	this.onFormLoaded();
      }
    );
  }

  /** Method triggered on change of suite input.
   * */
  suiteDropdownChanged(suiteName: string) {
    this.suiteName = suiteName;
    this.suiteSelected = true
    this.resetDeviceInput();
    this.isReadyToRun();
  }

  /** Method checking the `string` is empty or null. */
  private checkIsEmpty(s: null | string): boolean {
      return s === null || (s && s.trim() === '');
  }

  /** Method triggered on change of suite input and dut ip */
  private resetDeviceInput() {
    this.deviceIdSelector?.clearSelection();
    this.deviceInput?.clear();
    this.device = null;
  }

  /** Method triggered on changing of device id **/
  public deviceIdChanged(event: MatSelectChange) {
      this.device_id = event.value;
      if (this.peripherals_info_json['Devices'] !== null) {
          this.device = this.getDeviceBy(this.device_id);
      }
      this.isReadyToRun();
  }

  /** Method triggered on changing of device version or file **/
  public deviceInputChanged() {
      this.device_file_or_version = this.deviceInput?.getInput()?.trim();
      this.isReadyToRun();
  }

  /** Method triggered on changing of certificate ID **/
  public certificateIdInputChanged() {
      this.cert_id = this.certificateIdInput?.getInput()?.trim();
      this.isReadyToRun();
  }

  /** Method triggered on change of DUT IP input.
   * */
  dutIPDropdownChanged(dut_ip: string) {
    this.dut_IP = dut_ip
    this.data = [];
    this.peripheral_error = false;
    this.peripherals_info_json = null;
    this.resetDeviceInput();
    this.onFormLoading("fetching devices...");
    this.moblabGrpcService.getPeripheralInformation(
      dut_ip,
      (response: GetPeripheralInformationResponse) => {
        console.log('successfully got the result back with response:')
        console.log(response.getJsonInfo())
        this.peripherals_info_json = JSON.parse(response.getJsonInfo());
        if (this.peripherals_info_json['Devices'] !== null) {
            this.data = this.peripherals_info_json['Devices'].map(device => {
                return new SelectableItem(
                    `${device.Name}`,
                    device.Flags.includes('updatable') ? '' : '(not-updatable)',
                    `${device.DeviceId}`
                );
            });
        }
	this.onFormLoaded();
        this.suiteSelectForm.enable();
      },
      (message: string) => {
	this.onFormLoaded();
	this.peripheral_error = true;
      }
    )
  }

  public refresh_peripheral_information() {
    if (this.dut_IP) {
      this.dutIPDropdownChanged(this.dut_IP);
    }
  }

  isReadyToRun() {
    const isDeviceSelected = !this.checkIsEmpty(this.device_id);
    let isDeviceValid = false;
    switch (this.suiteName) {
        case this.FWUPD_UPDATE:
        case this.FWUPD_DOWNGRADE:
            isDeviceValid = isDeviceSelected;
            break;
        case this.FWUPD_INSTALL_VERSION:
        case this.FWUPD_INSTALL_FILE:
            isDeviceValid = isDeviceSelected && !this.checkIsEmpty(this.device_file_or_version);
            break;
    }

    if (this.suiteSelected && this.buildSelected && isDeviceValid) {
      this.runSuiteButton.enable();
    } else {
      this.runSuiteButton.disable();
    }
  }

  /** Method triggered on complete setting of build-related arguments.
   * ( model, build-target, milestone, build-version ).
   * */
  onBuildSetCustom(event) {
    this.buildSelected = true;
    this.dutSelectForm.enable();
    this.getConnectedDuts()
    this.isReadyToRun();
  }

  /** Method is triggered when build version form no longer has a valid
   * build version selected.
   * */
  onBuildVersionUnselected() {
    this.buildSelected = false;
    this.isReadyToRun();
  }

  /** Method to get the device */
  private getDeviceBy(device_id: string): keyable | null {
    return this.peripherals_info_json['Devices']
                        .find(device => device.DeviceId === device_id) ?? null;
  }

  /** Method is getting the `test_args` **/
  private getTestArgs(): string[] {
    let id = (this.device?.Guid[0] ?? this.getDeviceBy(this.device_id)?.Guid[0]) || this.device_id;

    return [
      `device_id=${id}`,
      ... (this.suiteName === this.FWUPD_INSTALL_VERSION) ? [`version=${this.device_file_or_version}`] : [],
      ... (this.suiteName === this.FWUPD_INSTALL_FILE) ? [`fwfile=${this.device_file_or_version}`] : [],
      ... (this.cert_id) ? [`cert_id=${this.cert_id}`] : [],
    ];
  }


  /** Method triggered on run-suite button press. Invokes runSuite RPC call.
   * */
  onRunSuiteClick() {
    super.onRunSuiteClick('Starting suite run.');

    this.moblabGrpcService.runFWUPDSuite(
      _ => {
        this.onSuiteStarted();
      },
      (err, _) => {
        this.onRunSuiteFailed(err.message);
        this.isReadyToRun();
      },
      this.suiteName,
      this.selectedBuild,
      this.selectedMilestone,
      this.selectedBoard,
      this.selectedModel,
      this.selectedPool,
      this.getTestArgs(),
    );
  }
}
