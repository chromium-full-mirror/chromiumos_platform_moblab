import {AfterContentInit, Component, ViewChild} from '@angular/core';

import {Router} from '@angular/router';

import {BaseSuite} from '../../common/base_suite/base-suite.component';
import {BasicTextFormComponent} from '../../common/basic-text-form/basic-text-form.component';
import {BuildSettings} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from './../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {BasicSelectorComponent} from '../../common/basic-selector/basic-selector.component';
import {
  NotificationBannerComponent
} from 'app/widgets/notification-banner/notification-banner.component';

/** Component owns logic for CTS suite run form.
 * */
@Component({
  selector: 'app-cts-run',
  templateUrl: './cts-run.component.html',
  styleUrls: ['./cts-run.component.scss'],
})
export class CtsRunComponent extends BaseSuite implements AfterContentInit {
  @ViewChild('versionSelector') versionSelectForm;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;
  @ViewChild(BasicTextFormComponent) modulesTextForm;
  @ViewChild(BasicSelectorComponent) ctsVersionSelectorForm;

  suiteName: string;

  constructor(
    moblabGrpcService: MoblabGrpcService,
    router: Router,
    notificationBanner: NotificationBannerComponent,
  ) {
    super(moblabGrpcService, router, notificationBanner);
  }

  /** Sets initial form enable/disable states.
   * */
  ngAfterContentInit(): void {
    setTimeout(() => {
      this.versionSelectForm.disable('Please select build.');
      this.modulesTextForm.disable('Please select build.');
    });
  }

  /** Method is triggered when build version form no longer has a valid
   * build version selected.
   * */
  onBuildVersionUnselected() {
    this.ctsVersionSelectorForm.clearSelection();
    this.ctsVersionSelectorForm.disable();
    this.runSuiteButton.disable();
  }

  /** Method triggered on change of the cts version form.
   * */
  ctsVersionChanged(suiteName: string) {
    if (suiteName === 'cts_R') {
      this.suiteName = 'cts';
    } else {
      this.suiteName = suiteName;
    }
    this.runSuiteButton.enable();
  }

  /** Method triggered on complete setting of build-related arguments.
   * ( model, build-target, milestone, build-version ).
   * */
  onBuildSetCustom(event) {
    this.modulesTextForm.enable();
    this.versionSelectForm.enable();
  }

  /** Method triggered on run-suite button press. Invokes runCtsSuite RPC call.
   * */
  onRunSuiteClick() {
    super.onRunSuiteClick('Starting CTS suite run.');

    this.moblabGrpcService.runCtsSuite(
      response => {
        this.onSuiteStarted();
      },
      (err, response) => {
        this.onRunSuiteFailed(err.message);
        this.runSuiteButton.enable();
      },
      this.suiteName,
      this.selectedBuild,
      this.selectedMilestone,
      this.selectedBoard,
      this.selectedModel,
      this.selectedPool,
      this.modulesTextForm.getCsvList()
    );
  }
}
