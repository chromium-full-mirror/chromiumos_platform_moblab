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
import {NotificationsService} from 'app/services/notifications.service';

@Component({
  selector: 'app-pvs',
  templateUrl: './pvs.component.html',
  styleUrls: ['./pvs.component.scss'],
})
export class PvsComponent extends BaseSuite implements AfterViewInit {
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

  public suiteList: string[] = [
    'sanity',
    'pvs-tast-cq',
    'bvt-cq',
    'bvt-inline',
    'thermal_qual_fast',
    'thermal_qual_full',
    'pvs-audio',
    'pvs-graphics',
    'pvs-video',
    'pvs-display',
    'pvs-kernel',
  ];

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
    this.changeDetector.detectChanges();
  }

  /** Method triggered on change of suite input form.
   * */
  suiteChanged() {
    this.suiteSelected = this.suiteName ? true : false;
    this.isReadyToRun();
  }

  /** Method triggered on change of suite input form.
   * */
  suiteDropdownChanged(suiteName: string) {
    this.suiteName = suiteName;

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
