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

/** Component owns logic for hardware memory qualification suite run form.
 * */
@Component({
  selector: 'app-memory-qual',
  templateUrl: './memory-qual.component.html',
  styleUrls: ['./memory-qual.component.scss'],
})
export class MemoryQualComponent extends BaseSuite implements AfterViewInit {
  @ViewChild('bugIdInput') bugIdInput;
  @ViewChild('partNumberInput') partNumberInput;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

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

  /** Method triggered on complete setting of build-related arguments.
   * ( model, build-target, milestone, build-version ).
   * */
  onBuildSetCustom(event) {
    this.bugIdInput.enable();
    this.partNumberInput.enable();
  }

  /** Method triggered on change of either bug ID or part number.
   * */
  avlInputChanged() {
    if (this.bugIdInput.getInput() && this.partNumberInput.getInput()) {
      this.runSuiteButton.enable();
    } else {
      this.runSuiteButton.disable();
    }
  }

  /** Method is triggered when build version form no longer has a valid
   * build version selected.
   * */
  onBuildVersionUnselected() {
    this.runSuiteButton.disable();
  }

  /** Method triggered on run-suite button press. Invokes
   *  runMemoryQualificationSuite RPC call.
   * */
  onRunSuiteClick() {
    super.onRunSuiteClick('Starting memory qualification suite run.');

    this.moblabGrpcService.runMemoryQualificationSuite(
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
      this.partNumberInput.getInput()
    );
  }
}
