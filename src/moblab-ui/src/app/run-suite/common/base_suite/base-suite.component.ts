import {Component, EventEmitter, Output} from '@angular/core';

import {Router} from '@angular/router';

import {JOB_START_TIME_FROM_FILTER} from '../../../view-jobs/view-jobs.component';
import {MoblabGrpcService} from '../../../services/moblab-grpc.service';
import {normalizeTimestamp} from '../../../utils/date';
import {
  NotificationBannerComponent
} from 'app/widgets/notification-banner/notification-banner.component';

export interface BuildSettings {
  build: string;
  board: string;
  model: string;
  milestone: string;
  buildVersionName: string;
  pool: string;
}

export enum SuiteChangeType {
  RunSuiteStart = 1,
  RunSuiteFailed,
  FormLoadingStart,
  FormLoadingFinish,
}

/**
 * Base class meant to parent all implementations of run suite logic. Contains
 * some logic that is common to all suites.
 */
@Component({template: ''})
export abstract class BaseSuite {
  @Output() suiteFormChange = new EventEmitter();

  runSuiteButtonDisabled = true;

  selectedBuild = '';
  selectedBoard = '';
  selectedMilestone = '';
  selectedModel = '';
  selectedPool = '';

  constructor(
    public moblabGrpcService: MoblabGrpcService,
    public router: Router,
    private notificationBanner: NotificationBannerComponent,
  ) { }

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

  onFormLoading(event: Event) {
    this.suiteFormChange.emit({
      changeType: SuiteChangeType.FormLoadingStart,
      message: event,
    });
  }

  onFormLoaded() {
    this.suiteFormChange.emit({changeType: SuiteChangeType.FormLoadingFinish});
  }

  onRunSuiteClick(message = '') {
    if (message !== '') {
      this.notificationBanner.notify(message);
    }

    this.suiteFormChange.emit({changeType: SuiteChangeType.RunSuiteStart});
  }

  onRunSuiteFailed(message = '') {
    if (message !== '') {
      this.notificationBanner.error(message);
    }
    this.suiteFormChange.emit({changeType: SuiteChangeType.RunSuiteFailed});
  }

  onSuiteStarted() {
    this.redirectToViewJobs();
  }

  redirectToViewJobs() {
    const params = {};
    params[JOB_START_TIME_FROM_FILTER] = normalizeTimestamp(
      new Date().setTime(new Date().getTime() - 1000 /* 1 second */)
    );
    this.router.navigate(['/view_jobs'], {queryParams: params});
  }
}
