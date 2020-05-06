import {MatSnackBar} from '@angular/material/snack-bar';
import {Router} from '@angular/router';

import {MoblabGrpcService} from '../../../services/moblab-grpc.service';


export interface BuildSettings {
  build: string;
  board: string;
  model: string;
  milestone: string;
  buildVersionName: string;
  pool: string;
}

/**
 * Base class meant to parent all implementations of run suite logic. Contains
 * some logic that is common to all suites.
 */
export abstract class BaseSuite {
  runSuiteButtonDisabled = true;

  selectedBuild: string;
  selectedBoard: string;
  selectedModel: string;
  selectedPool: string;

  constructor(public moblabGrpcService: MoblabGrpcService,
              public router: Router,
              public snackBar: MatSnackBar) {
  }

  onBuildSet(event: BuildSettings) {
    this.selectedModel = event.model;
    this.selectedBuild = event.build;
    this.selectedBoard = event.board;
    this.selectedPool = event.pool;
    this.onBuildSetCustom(event);
  }

  /**
   * Method that defines what happens when model/build/build version are selected
   * for suite run. Generally is enabling of another, suite-specific form.
   */
  abstract onBuildSetCustom(event: BuildSettings);

  /**
   * Method that defines when the runSuite button is pressed, generally is a
   * Moblab RPC call.
   */
  abstract onRunSuite();

  redirectToViewJobs() {
    this.router.navigate(['/view_jobs']);
  }

  setOffPopup(dialogue: string) {
    const snackBarRef = this.snackBar.open(dialogue, '', {
      duration: 5000,
      verticalPosition: 'top',
      panelClass: ['action-submission-popup'],
    });
  }
}
