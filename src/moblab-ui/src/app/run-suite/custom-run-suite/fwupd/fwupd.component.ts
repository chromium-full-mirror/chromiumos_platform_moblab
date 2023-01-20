import {
  AfterContentInit, 
  AfterViewInit, 
  ChangeDetectorRef, 
  Component, 
  ViewChild
} from '@angular/core';

import {Router} from '@angular/router';
import {MatTableDataSource} from '@angular/material/table';

import {BaseSuite} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from '../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {BasicSelectorComponent} from '../../common/basic-selector/basic-selector.component';
import {NotificationsService} from '../../../services/notifications.service';
import {BuildTargetAccessService} from '../../../services/build-target-access.service';
import {ConnectedDutInfo, GetPeripheralInformationResponse} from '../../../services/moblabrpc_pb';

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
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

  public peripherals_info_json: JSON;
  public peripherals_info_stringified: string;
  public test_args: string[] = [];
  public dutIPs: string[] = [];
  public suiteList: string[] = [
    'fwupd_test_suite_1',
    'fwupd_test_suite_2'
  ];

  public suiteName = '';
  private buildSelected = false;
  private suiteSelected = false;

  public dut_IP = '';
  
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

  filterEnrolledDuts(connectedDuts: ConnectedDutInfo[]) {
    const enrolledDuts = connectedDuts;
    this.dutIPs = connectedDuts
      .filter(Dut => Dut.getIsEnrolled())
      .map(Dut => Dut.getIp());;
  }

  getConnectedDuts() {
    this.moblabGrpcService.listConnectedDuts(
      (connectedDuts: ConnectedDutInfo[]) => {
        this.filterEnrolledDuts(connectedDuts);
      },
      (message: string) => {
        this.filterEnrolledDuts([]);
        this.onRunSuiteFailed(message);
      }
    );
  }

  /** Method triggered on change of suite input.
   * */
  suiteDropdownChanged(suiteName: string) {
    this.suiteName = suiteName;
    this.suiteSelected = true
    this.isReadyToRun();
  }

  /** Method triggered on change of DUT IP input.
   * */
   dutIPDropdownChanged(dut_ip: string) {
    this.dut_IP = dut_ip
    this.moblabGrpcService.getPeripheralInformation(
      dut_ip,
      (response: GetPeripheralInformationResponse) => {
        console.log('successfully got the result back with response:')
        console.log(response.getJsonInfo())
        this.peripherals_info_json = JSON.parse(response.getJsonInfo());
        this.peripherals_info_stringified = JSON.stringify(this.peripherals_info_json, null, 2);
        this.suiteSelectForm.enable();
      },
      (message: string) => {
        this.onRunSuiteFailed(message);
      }
    )
  }

  isReadyToRun() {
    if (this.suiteSelected && this.buildSelected) {
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
      this.test_args
    );
  }
}
