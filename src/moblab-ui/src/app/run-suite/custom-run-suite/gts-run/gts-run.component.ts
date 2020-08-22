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
import {MoblabGrpcService} from './../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';


/** Component owns logic for GTS suite run form.
 * */
@Component({
  selector: 'app-gts-run',
  templateUrl: './gts-run.component.html',
})
export class GtsRunComponent extends BaseSuite implements AfterViewInit {
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;
  @ViewChild(BasicTextFormComponent) modulesTextForm;

  constructor(private changeDetector: ChangeDetectorRef,
              moblabGrpcService: MoblabGrpcService,
              router: Router,
              snackBar: MatSnackBar) {
    super(moblabGrpcService, router, snackBar);
  }

  /** Sets initial form enable/disable states.
   * */
  ngAfterViewInit(): void {
    this.modulesTextForm.disable('Please select build.');
    this.changeDetector.detectChanges();
  }

  /** Method triggered on complete setting of build-related arguments.
   * ( model, build-target, milestone, build-version ).
   * */
  onBuildSetCustom(event) {
    this.modulesTextForm.enable();
    this.runSuiteButton.enable();
  }

  /** Method triggered on run-suite button press. Invokes runGtsSuite RPC call.
   * */
  onRunSuiteClick() {
    super.onRunSuiteClick('Starting GTS suite run.');

    this.moblabGrpcService.runGtsSuite(
      (response) => {
        this.onSuiteStarted();
      },
      (err, response) => {
        this.setOffPopup(err.message);
        this.runSuiteButton.enable();
      },
      this.selectedBuild,
      this.selectedMilestone,
      this.selectedBoard,
      this.selectedModel,
      this.selectedPool,
      this.modulesTextForm.getCsvList(),
    );
  }
}
