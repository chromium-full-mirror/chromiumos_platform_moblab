import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  ViewChild
} from '@angular/core';

import {MatSnackBar} from '@angular/material/snack-bar';
import {Router} from '@angular/router';

import {BaseSuite} from '../../common/base_suite/base-suite.component';
import {BasicTextFormComponent} from '../../common/basic-text-form/basic-text-form.component';
import {BuildSettings} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from './../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {BasicSelectorComponent} from '../../common/basic-selector/basic-selector.component';


/** Component owns logic for CTS suite run form.
 * */
@Component({
  selector: 'app-cts-run',
  templateUrl: './cts-run.component.html',
  styleUrls: ['./cts-run.component.scss'],
})
export class CtsRunComponent extends BaseSuite implements AfterViewInit {
  @ViewChild('versionSelector') versionSelectForm;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;
  @ViewChild(BasicTextFormComponent) modulesTextForm;
  @ViewChild(BasicSelectorComponent) ctsVersionSelectorForm;

  selectedAndroidVersion: string;

  constructor(private changeDetector: ChangeDetectorRef,
    moblabGrpcService: MoblabGrpcService,
    router: Router,
    snackBar: MatSnackBar) {
    super(moblabGrpcService, router, snackBar);
  }

  /** Sets initial form enable/disable states.
   * */
  ngAfterViewInit(): void {
    this.versionSelectForm.disable('Please select build.');
    this.modulesTextForm.disable('Please select build.');
    this.changeDetector.detectChanges();
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
  ctsVersionChanged(selectedAndroidVersion: string) {
    this.selectedAndroidVersion = selectedAndroidVersion;
    this.runSuiteButton.enable();
  }

  /** Method triggered on complete setting of build-related arguments.
   * ( model, build-target, milestone, build-version ).
   * */
  onBuildSetCustom(event: BuildSettings) {
    this.modulesTextForm.enable();
    this.versionSelectForm.enable();
  }

  /** Method triggered on run-suite button press. Invokes runCtsSuite RPC call.
   * */
  onRunSuiteClick() {
    super.onRunSuiteClick('Starting CTS suite run.');

    this.moblabGrpcService.runCtsSuite(
      (response) => {
        this.onSuiteStarted();
      },
      (err, response) => {
        this.onRunSuiteFailed(err.message);
        this.runSuiteButton.enable();
      },
      this.selectedAndroidVersion,
      this.selectedBuild,
      this.selectedMilestone,
      this.selectedBoard,
      this.selectedModel,
      this.selectedPool,
      this.modulesTextForm.getCsvList(),
    );
  }
}
