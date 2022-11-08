import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  ViewChild,
} from '@angular/core';

import {Router} from '@angular/router';

import {BaseSuite} from '../common/base_suite/base-suite.component';
import {MoblabGrpcService} from './../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../common/run-suite-button/run-suite-button.component';
import {NotificationsService} from 'app/services/notifications.service';

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

  MANUAL_SUITE_ENTRY_DESC = '>> Enter suite name';
  public suiteList: string[] = [
    this.MANUAL_SUITE_ENTRY_DESC,
    'au_fsi',
    'bvt-cq',
    'bvt-inline',
    'bvt-tast-cq',
    'camera-usb-qual',
    'wifi_matfunc',
    'wifi_perf',
    'labqual',
    'thermal_qual_fast',
    'thermal_qual_full',
    'performance_cuj_v2',
    'performance_cuj_quick_v2',
    'performance_cuj',
    'performance_cuj_quick',
    'mtbf',
  ];

  public hideCustomInput = true;

  public suiteName = '';
  private buildSelected = false;
  private suiteSelected = false;

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
    this.suiteInput.disable('Please select build.');
    this.changeDetector.detectChanges();
  }

  /** Method triggered on change of suite input form.
   * */
  suiteChanged() {
    this.suiteName = this.suiteInput.getInput();
    this.suiteSelected = this.suiteName ? true : false;
    this.isReadyToRun();
  }

  /** Method triggered on change of suite input form.
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
    this.suiteSelected = this.suiteName ? true : false;
    this.isReadyToRun();
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
    this.suiteInput.enable();
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

    this.moblabGrpcService.runSuite(
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
      this.selectedPool
    );
  }
}
