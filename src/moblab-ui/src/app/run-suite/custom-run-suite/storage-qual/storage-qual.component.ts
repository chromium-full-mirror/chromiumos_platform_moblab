import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  ViewChild
} from '@angular/core';

import {BaseSuite} from '../../common/base_suite/base-suite.component';
import {MoblabGrpcService} from './../../../services/moblab-grpc.service';
import {RunSuiteButtonComponent} from '../../common/run-suite-button/run-suite-button.component';
import {Router} from '@angular/router';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-storage-qual',
  templateUrl: './storage-qual.component.html',
  styleUrls: ['./storage-qual.component.scss']
})
export class StorageQualComponent extends BaseSuite implements AfterViewInit {
  @ViewChild('bugIdInput') bugIdInput;
  @ViewChild('partNumberInput') partNumberInput;
  @ViewChild(RunSuiteButtonComponent) runSuiteButton;

  constructor(private changeDetector: ChangeDetectorRef,
              moblabGrpcService: MoblabGrpcService,
              router: Router,
              snackBar: MatSnackBar) {
    super(moblabGrpcService, router, snackBar);
  }

  /** Sets initial form enable/disable states.
   * */
  ngAfterViewInit(): void {
    this.bugIdInput.disable('Please select build.');
    this.partNumberInput.disable('Please select build.');
    this.changeDetector.detectChanges();
  }

  onBuildSetCustom(event) {
    this.bugIdInput.enable();
    this.partNumberInput.enable();
    this.runSuiteButton.enable();
  }

  /** Method triggered on change of either bug ID or part number.
   * */
  avlInputChanged(event) {
    if (this.bugIdInput.getInput() && this.partNumberInput.getInput()) {
      this.runSuiteButton.enable();
    } else {
      this.runSuiteButton.disable();
    }
  }

  /** Method triggered on run-suite button press. Invokes
   *  runStorageQualificationSuite RPC call.
   * */
  onRunSuite() {
    this.moblabGrpcService.runStorageQualificationSuite(
      (response) => {
        this.redirectToViewJobs();
      },
      (err, response) => {
        this.setOffPopup(err.message);
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
