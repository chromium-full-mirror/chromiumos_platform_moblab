import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  Input,
  OnDestroy,
  OnInit,
  ViewChild,
} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {DatePipe} from '@angular/common';
import {FormControl} from '@angular/forms';
import {MatPaginator} from '@angular/material/paginator';
import {MatTableDataSource} from '@angular/material/table';
import {Sort} from '@angular/material/sort';
import {MatSlideToggleChange} from '@angular/material/slide-toggle';
import {Subscription, timer} from 'rxjs';

import {
  forbiddenDateValidator,
  forbiddenIDValidator,
} from '../utils/validators';
import {INT_TO_PRIORITY, INT_TO_JOBSTATUS} from '../utils/proto_helpers';
import {Job} from '../services/moblabrpc_pb';
import {JobActionComponent} from './job-action/job-action.component';
import {MoblabGrpcService} from '../services/moblab-grpc.service';
import {normalizeTimestamp, datestringToSecondsTimestamp} from '../utils/date';
import {TableHeaderSelectorComponent} from '../widgets/table-header-selector/table-header-selector.component';
import {NotificationsService} from 'app/services/notifications.service';

export const JOB_NAME = 'name';
export const JOB_ID = 'id';
export const JOB_PRIORITY = 'priority';
export const QUEUE_STATUS = 'queueStatus';
export const JOB_RELATIONSHIP = 'relationship';
export const JOB_START_TIME_FROM_FILTER = 'startTimeFromFilter';
export const JOB_START_TIME_TO_FILTER = 'startTimeToFilter';
export const PARENT_JOB_ID = 'parent_job_id';
export const DUT_RUN_ON = 'dut_run_on';
export const FILTER_PARAMETERS = [
  JOB_NAME,
  JOB_ID,
  JOB_PRIORITY,
  QUEUE_STATUS,
  JOB_RELATIONSHIP,
  JOB_START_TIME_FROM_FILTER,
  JOB_START_TIME_TO_FILTER,
  PARENT_JOB_ID,
  DUT_RUN_ON,
];
const FILTER_VALIDATORS = {};

FILTER_VALIDATORS[JOB_START_TIME_FROM_FILTER] = [forbiddenDateValidator];
FILTER_VALIDATORS[JOB_START_TIME_TO_FILTER] = [forbiddenDateValidator];
FILTER_VALIDATORS[JOB_ID] = [forbiddenIDValidator];
FILTER_VALIDATORS[PARENT_JOB_ID] = [forbiddenIDValidator];

const DEFAULT_PAGE_SIZE = 20;

/*
  For handling multiple filter forms without having to repeat logic per
  FormControl.
*/
export class MultiFilterForm {
  formControls = {};

  constructor(private filterParameters: string[]) {
    for (const filterName of filterParameters) {
      this.formControls[filterName] = new FormControl(
        '',
        filterName in FILTER_VALIDATORS ? FILTER_VALIDATORS[filterName] : []
      );
    }
  }

  getFormControl(filterName: string) {
    return this.formControls[filterName];
  }

  getFormValue(filterName: string) {
    return this.getFormControl(filterName).value;
  }

  setFormValue(filterName: string, value: string | undefined) {
    this.getFormControl(filterName).setValue(value);
  }

  anyErrors() {
    for (const filterName in this.formControls) {
      if (this.getFormControl(filterName).errors) {
        return true;
      }
    }
    return false;
  }

  reset() {
    for (const filterName in this.formControls) {
      this.formControls[filterName].setValue('');
    }
  }
}

export class UploadStatus {
  constructor(
    public icon = '',
    public iconStyle = '',
    public tooltip = '',
    public attemptNumber = ''
  ) {}
}

@Component({
  selector: 'app-view-jobs',
  templateUrl: './view-jobs.component.html',
  styleUrls: ['./view-jobs.component.scss'],
  providers: [DatePipe],
})
export class ViewJobsComponent implements OnDestroy, OnInit, AfterViewInit {
  @Input() manualPopulate = false;
  @Input() hideActionBar = false;
  @Input() hideFilters = false;
  @Input() hideSelectors = false;
  @Input() pageSizeOverride = 0;
  @Input() filtersOverride: MultiFilterForm;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(JobActionComponent) jobActionRef: JobActionComponent;
  @ViewChild(TableHeaderSelectorComponent)
  tableHeadSelectorRef: TableHeaderSelectorComponent;
  displayedColumns: string[] = [
    'job_id',
    'hostname',
    'name',
    'priority',
    'created_time_sec_utc',
    //TO-DO(wangmichael) reintroduce these columns once backend is swapped from
    // AFE to something that actually returns these values.
    // 'start_time_sec_utc',
    // 'finished_time_sec_utc',
    'job_status',
    'job_upload_status',
    'logs',
  ];
  jobSelectOptions: string[] = ['Visible'];
  jobs = new MatTableDataSource<Job>();
  sortBy = '';
  autoRefresh = false;

  loading = false;
  numJobs = 0;
  expandedElement: Job | null = null;
  startingPageSize = 0;

  filters = new MultiFilterForm(FILTER_PARAMETERS);
  jobId: string = JOB_ID;
  jobName: string = JOB_NAME;
  parentJobId: string = PARENT_JOB_ID;
  jobPriority: string = JOB_PRIORITY;
  queueStatus: string = QUEUE_STATUS;
  jobRelationship: string = JOB_RELATIONSHIP;
  jobStartTimeFromFilter: string = JOB_START_TIME_FROM_FILTER;
  jobStartTimeToFilter: string = JOB_START_TIME_TO_FILTER;

  jobs_queued = 0;
  jobs_running = 0;
  jobs_completed = 0;
  jobs_aborted = 0;
  jobs_failed = 0;
  jobs_total = 0;

  normalizeTimestamp = normalizeTimestamp;

  private getJobsSubscription: Subscription;

  // Removing the first, default value of each enum ( which represent the 'unset'
  // state.
  relationshipFilterOptions = [''].concat(
    Object.keys(Job.Relationship).slice(1)
  );
  queueStatusFilterOptions = [''].concat(Object.keys(Job.QueueStatus).slice(1));
  cloudBucketUrl = '';

  constructor(
    public readonly moblabGrpcService: MoblabGrpcService,
    private changeDetectorRefs: ChangeDetectorRef,
    private datePipe: DatePipe,
    private route: ActivatedRoute,
    private notificationsService: NotificationsService
  ) {
    this.moblabGrpcService
      .getCloudBucketUrl()
      .then(s => (this.cloudBucketUrl = s))
      .catch(e => notificationsService.error(e));
  }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.applyFilters(params);
    });

    this.startingPageSize = this.pageSizeOverride
      ? this.pageSizeOverride
      : DEFAULT_PAGE_SIZE;

    if (this.paginator) {
      this.paginator.pageSize = this.startingPageSize;
    }

    if (this.filtersOverride) {
      this.filters = this.filtersOverride;
    }

    if (!this.hideSelectors) {
      this.displayedColumns = ['job_checkboxes'].concat(this.displayedColumns);
    }
  }

  ngAfterViewInit() {
    if (!this.manualPopulate) {
      this.moblabGrpcService.getNumJobs((numJobs: number) => {
        this.numJobs = numJobs;
      });
      this.getNextPageJobs();
    }

    this.paginator.page.subscribe(() => this.getNextPageJobs());

    this.changeDetectorRefs.detectChanges();
    this.getJobsProgress();
  }

  applyFilters(params: {[x: string]: any}) {
    for (const filter_id of FILTER_PARAMETERS) {
      if (filter_id in params) {
        this.filters.getFormControl(filter_id).setValue(params[filter_id]);
      }
    }
  }

  selectionChanged(event: {selection: string}) {
    if (event.selection === 'All') {
      this.selectAllJobs();
    } else if (event.selection === 'Visible') {
      this.jobActionRef.clearSelectedJobs();
      this.jobs.data.forEach(this.jobActionRef.selectJob, this.jobActionRef);
    } else if (event.selection === 'None') {
      this.jobActionRef.clearSelectedJobs();
    }
  }

  getJobFilters() {
    /**
     * Method that collects and returns all filters relevant to querying jobs.
     * These filters are shared between getJobs, getNumJobs, and getJobIds
     * calls.
     */
    const job_id_filter = this.filters.getFormValue(JOB_ID);
    let job_name_filter = this.filters.getFormValue(JOB_NAME);
    if (job_name_filter !== job_name_filter.trim()) {
      job_name_filter = job_name_filter.trim();
      this.filters.setFormValue(JOB_NAME, job_name_filter);
    }
    const job_start_lt_filter = datestringToSecondsTimestamp(
      this.filters.getFormValue(JOB_START_TIME_TO_FILTER)
    );
    const job_start_gt_filter = datestringToSecondsTimestamp(
      this.filters.getFormValue(JOB_START_TIME_FROM_FILTER)
    );
    const job_queue_status_filter = this.filters.getFormValue(QUEUE_STATUS)
      ? Number(Job.QueueStatus[this.filters.getFormValue(QUEUE_STATUS)])
      : 0;
    const job_relationship_filter = this.filters.getFormValue(JOB_RELATIONSHIP)
      ? Number(Job.Relationship[this.filters.getFormValue(JOB_RELATIONSHIP)])
      : 0;
    const parent_id_filter = this.filters.getFormValue(PARENT_JOB_ID);
    const dut_filter = this.filters.getFormValue(DUT_RUN_ON);
    return [
      job_id_filter,
      job_name_filter,
      job_start_lt_filter,
      job_start_gt_filter,
      job_queue_status_filter,
      job_relationship_filter,
      parent_id_filter,
      dut_filter,
    ];
  }

  selectJobIds(job_ids: number[]) {
    this.jobActionRef.selectJobs(job_ids);
    this.getNextPageJobs();
    this.jobs.filteredData.forEach(
      this.jobActionRef.selectJob,
      this.jobActionRef
    );
  }

  selectAllJobs() {
    /**
     * Queries backend for list of job ids that meet filter parameters and
     * selects all returned jobs in job action component.
     */
    this.loading = true;

    const [
      job_id_filter,
      job_name_filter,
      job_start_lt_filter,
      job_start_gt_filter,
      job_queue_status_filter,
      job_relationship_filter,
      parent_id_filter,
      dut_filter,
    ] = this.getJobFilters();

    this.moblabGrpcService.getJobIds(
      (job_ids: number[]) => {
        this.selectJobIds(job_ids);
      },
      this.errorHandling,
      // get all jobs, so index 0
      0,
      // TO-DO: optimize get_ids so that cancelling 1000+ jobs wont be so
      // slow.
      1000,
      job_id_filter,
      job_name_filter,
      job_start_lt_filter,
      job_start_gt_filter,
      job_queue_status_filter,
      job_relationship_filter,
      parent_id_filter,
      dut_filter
    );
  }

  sortData(sort: Sort) {
    if (!sort.active || sort.direction === '') {
      this.sortBy = '';
      return;
    }

    const direction = sort.direction === 'desc' ? '-' : '';
    switch (sort.active) {
      case 'job_id':
        this.sortBy = direction + JOB_ID;
        break;
      case 'name':
        this.sortBy = direction + JOB_NAME;
        break;
      case 'priority':
        this.sortBy = direction + JOB_PRIORITY;
        break;
      case 'created_time_sec_utc':
        this.sortBy = direction + 'created_on';
        break;
      default:
        this.sortBy = '';
    }
    this.resetPagination();
    this.getNextPageJobs();
  }

  async getJobsProgress() {
    this.jobs_queued = await this.getNumJobsPromise(
      Number(Job.QueueStatus.QUEUED_JOBS)
    );
    this.jobs_running = await this.getNumJobsPromise(
      Number(Job.QueueStatus.JOBS_RUNNING)
    );
    this.jobs_completed = await this.getNumJobsPromise(
      Number(Job.QueueStatus.COMPLETED_JOBS)
    );
    this.jobs_aborted = await this.getNumJobsPromise(
      Number(Job.QueueStatus.ABORTED_JOBS)
    );
    this.jobs_failed = await this.getNumJobsPromise(
      Number(Job.QueueStatus.FAILED_JOBS)
    );
    this.jobs_total = await this.getNumJobsPromise();
  }

  getNumJobsPromise(statusFilter?): Promise<number> {
    /**
     * Convert the getNumJobs function into a Promise.
     */
    const [
      job_id_filter,
      job_name_filter,
      job_start_lt_filter,
      job_start_gt_filter,
      job_queue_status_filter,
      job_relationship_filter,
      parent_id_filter,
      dut_filter,
    ] = this.getJobFilters();

    if (job_queue_status_filter && job_queue_status_filter !== statusFilter) {
      return new Promise((resolve, _) => {
        resolve(0);
      });
    }

    return new Promise((resolve, _) => {
      this.moblabGrpcService.getNumJobs(
        (numJobs: number) => {
          resolve(numJobs);
        },
        job_id_filter,
        job_name_filter,
        job_start_lt_filter,
        job_start_gt_filter,
        statusFilter,
        job_relationship_filter,
        parent_id_filter,
        dut_filter
      );
    });
  }

  getPriorityFromNum(priorityNum: string | number) {
    return INT_TO_PRIORITY[priorityNum];
  }

  getStatusFromNum(statusNum: string | number) {
    return INT_TO_JOBSTATUS[statusNum];
  }

  getUploadStatus(job: Job) {
    const state = job.getUploadState();
    const status = state.getStatus();
    const attemptsBadge =
      state.getAttemptsNumber() > 1 ? state.getAttemptsNumber().toString() : '';
    const previousErrorMessage = state.getLastError();
    switch (status) {
      case Job.UploadStatus.UPLOAD_STATUS_UPLOADED:
      case Job.UploadStatus.UPLOAD_STATUS_DELETED:
        return new UploadStatus(
          'cloud_done',
          'norm-icon',
          'Uploaded successfully'
        );

      case Job.UploadStatus.UPLOAD_STATUS_QUEUED:
        return new UploadStatus(
          'cloud_queue',
          'norm-icon',
          'Ready to be uploaded'
        );

      case Job.UploadStatus.UPLOAD_STATUS_UPLOADING:
        return new UploadStatus(
          'cloud_upload',
          'progress-icon',
          'Uploading...',
          attemptsBadge
        );

      case Job.UploadStatus.UPLOAD_STATUS_UPLOAD_FAILED:
        return new UploadStatus(
          'cloud_upload',
          'error-icon',
          'Upload failed due to: ' + previousErrorMessage,
          attemptsBadge
        );

      case Job.UploadStatus.UPLOAD_STATUS_UNKNOWN:
      case Job.UploadStatus.UPLOAD_STATUS_NOT_READY:
      default:
        return new UploadStatus();
    }
  }

  isResultsDeleted(job: Job): boolean {
    return (
      job.getUploadState().getStatus() ===
      Job.UploadStatus.UPLOAD_STATUS_DELETED
    );
  }

  constructJobLogsLink(job: Job): string {
    if (this.isResultsDeleted(job)) {
      return `${this.cloudBucketUrl}/${job.getJobId()}-moblab/`;
    }
    return `${
      this.moblabGrpcService.service_address
    }/results/${job.getJobId()}-moblab/`;
  }

  assignJobs(jobs: Job[] | undefined) {
    this.jobs = new MatTableDataSource(jobs);
    this.loading = false;
  }

  resetPagination() {
    if (this && this.paginator) {
      this.paginator.pageIndex = 0;
    }
  }

  filterByStatus(status) {
    if (status !== 'ALL_JOBS') {
      this.filters.getFormControl(QUEUE_STATUS).setValue(status.value);
    }
    this.resetPagination();
    this.getNextPageJobs();
  }

  filterSubmission() {
    this.resetPagination();
    this.getNextPageJobs();
    this.getJobsProgress();
  }

  clearFilters() {
    this.filters.reset();
  }

  public setDutIp(ip: string) {
    this.filters.setFormValue(DUT_RUN_ON, ip);
  }

  public setParentJobId(id: string) {
    this.filters.setFormValue(PARENT_JOB_ID, id);
  }

  refreshJobs(parentJobId?: string, dutRunOn?: string) {
    this.resetPagination();
    this.getNextPageJobs();
    this.getJobsProgress();
  }

  getNextPageJobs() {
    /**
     * Refreshes jobs table according to filter and paginator parameters.
     */
    this.loading = true;
    const [
      job_id_filter,
      job_name_filter,
      job_start_lt_filter,
      job_start_gt_filter,
      job_queue_status_filter,
      job_relationship_filter,
      parent_id_filter,
      dut_filter,
    ] = this.getJobFilters();

    this.unsubscribeGetJobs();
    if (this.autoRefresh) {
      this.getJobsSubscription = timer(500, 60000).subscribe(() => {
        this.getJobs(
          job_id_filter,
          job_name_filter,
          job_start_lt_filter,
          job_start_gt_filter,
          job_queue_status_filter,
          job_relationship_filter,
          parent_id_filter,
          dut_filter,
          this.sortBy
        );
      });
    } else {
      this.getJobs(
        job_id_filter,
        job_name_filter,
        job_start_lt_filter,
        job_start_gt_filter,
        job_queue_status_filter,
        job_relationship_filter,
        parent_id_filter,
        dut_filter,
        this.sortBy
      );
    }
  }

  getJobs(
    jobIdFilter: string,
    jobNameFilter: string,
    jobStartLtFilter: number,
    jobStartGtFilter: number,
    jobQueueStatusFilter: Job.QueueStatus,
    jobRelationshipFilter: Job.Relationship,
    parentIdFilter: string,
    dutFilter: string,
    sortBy: string
  ) {
    this.moblabGrpcService.getJobs(
      (jobs: Job[]) => this.assignJobs(jobs),
      (message: string) => this.errorHandling(message),
      this.paginator && this.paginator.pageIndex
        ? this.paginator.pageIndex * this.paginator.pageSize
        : 0,
      this.paginator && this.paginator.pageSize
        ? this.paginator.pageSize
        : DEFAULT_PAGE_SIZE,
      jobIdFilter,
      jobNameFilter,
      jobStartLtFilter,
      jobStartGtFilter,
      jobQueueStatusFilter,
      jobRelationshipFilter,
      parentIdFilter,
      dutFilter,
      sortBy
    );

    this.moblabGrpcService.getNumJobs(
      (numJobs: number) => {
        this.numJobs = numJobs;
      },
      jobIdFilter,
      jobNameFilter,
      jobStartLtFilter,
      jobStartGtFilter,
      jobQueueStatusFilter,
      jobRelationshipFilter,
      parentIdFilter,
      dutFilter
    );
  }

  getNumVisibleJobs() {
    return this.jobs.data.length;
  }

  getNumSelectedJobs() {
    return this.jobActionRef.getNumSelectedJobs();
  }

  displayColumn(columnName: string) {
    return this.displayedColumns.includes(columnName);
  }

  updateAutoRefresh(toggle: MatSlideToggleChange) {
    this.unsubscribeGetJobs();
    this.autoRefresh = toggle.checked;
    if (toggle.checked) {
      this.getNextPageJobs();
      this.getJobsProgress();
    }
  }

  unsubscribeGetJobs() {
    if (this.getJobsSubscription && !this.getJobsSubscription.closed) {
      this.getJobsSubscription.unsubscribe();
    }
  }

  /*
    Stops redirect to job-details page from happening when the user selects a job's
    checkbox.
  */
  checkboxClick(e: {stopPropagation: () => void}) {
    e.stopPropagation();
  }

  errorHandling(message: string) {
    this.loading = false;
    this.notificationsService.error(message);
  }

  isAllJobsSelected() {
    return this.jobActionRef.getNumSelectedJobs() === this.jobs.data.length;
  }

  ngOnDestroy(): void {
    this.paginator.page.unsubscribe();
    this.unsubscribeGetJobs();
  }

  setDutFilter(dut: string) {
    this.filters.setFormValue(DUT_RUN_ON, dut);
  }
}
