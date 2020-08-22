import {
  EventEmitter,
  Output
} from '@angular/core';

import {MatSnackBar} from '@angular/material/snack-bar';
import {Router} from '@angular/router';

import {JOB_START_TIME_FROM_FILTER} from '../../../view-jobs/view-jobs.component';
import {MoblabGrpcService} from '../../../services/moblab-grpc.service';
import {normalizeTimestamp} from '../../../utils/date';

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
  @Output() suiteStarted = new EventEmitter();

  runSuiteButtonDisabled = true;

  selectedBuild: string;
  selectedBoard: string;
  selectedMilestone: string;
  selectedModel: string;
  selectedPool: string;

  constructor(public moblabGrpcService: MoblabGrpcService,
              public router: Router,
              public snackBar: MatSnackBar) {
  }

  onBuildSet(event: BuildSettings) {
    this.selectedModel = event.model;
    this.selectedBuild = event.build;
    this.selectedMilestone = event.milestone;
    this.selectedBoard = event.board;
    this.selectedPool = event.pool;
    this.onBuildSetCustom(event);
  }

  /**
   * Method that defines what happens when model/build/build version are selected
   * for suite run. Generally is enabling of another, suite-specific form.
   */
  abstract onBuildSetCustom(event: BuildSettings);

  onRunSuiteClick(submitMessage?: string) {
    this.setOffPopup(submitMessage);
    this.suiteStarted.emit();
  }

  onSuiteStarted() {
    this.redirectToViewJobs();
  }

  redirectToViewJobs() {
    const params = {};
    params[JOB_START_TIME_FROM_FILTER] = normalizeTimestamp(
      new Date().setTime(
        new Date().getTime()
        - 1000 /* 1 second */
      )
    );
    this.router.navigate(['/view_jobs'], { queryParams: params });
  }

  setOffPopup(dialogue: string) {
    const snackBarRef = this.snackBar.open(dialogue, '', {
      duration: 5000,
      verticalPosition: 'top',
      panelClass: ['action-submission-popup'],
    });
  }
}
