import {
  animate,
  state,
  style,
  transition,
  trigger,
} from '@angular/animations';
import {
  AfterContentInit,
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  HostListener,
  Input,
  OnDestroy,
  OnInit,
  ViewChild,
} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {DatePipe} from '@angular/common';
import {FormControl} from '@angular/forms';
import {MatPaginator} from '@angular/material/paginator';
import {MatSnackBar} from '@angular/material/snack-bar';
import {MatTableDataSource} from '@angular/material/table';

import {forbiddenDateValidator, forbiddenIDValidator} from '../utils/validators';
import {INT_TO_PRIORITY, INT_TO_JOBSTATUS} from '../utils/proto_helpers';
import {Job, Execution} from '../services/moblabrpc_pb';
import {JobActionComponent} from './job-action/job-action.component';
import {MoblabGrpcService} from '../services/moblab-grpc.service';
import {normalizeTimestamp, datestringToSecondsTimestamp} from '../utils/date';
import {TableHeaderSelectorComponent} from '../widgets/table-header-selector/table-header-selector.component';


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
  DUT_RUN_ON
];
const FILTER_VALIDATORS = {};

FILTER_VALIDATORS[JOB_START_TIME_FROM_FILTER] = [forbiddenDateValidator];
FILTER_VALIDATORS[JOB_START_TIME_TO_FILTER] = [forbiddenDateValidator];
FILTER_VALIDATORS[JOB_ID] = [forbiddenIDValidator];

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
        filterName in FILTER_VALIDATORS ? FILTER_VALIDATORS[filterName] : []);
    }
  }

  getFormControl(filterName) {
    return this.formControls[filterName];
  }

  getFormValue(filterName) {
    return this.getFormControl(filterName).value;
  }

  setFormValue(filterName, value) {
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

@Component({
  selector: 'app-view-jobs',
  templateUrl: './view-jobs.component.html',
  styleUrls: ['./view-jobs.component.css'],
  providers: [DatePipe]
})
export class ViewJobsComponent implements OnDestroy, OnInit, AfterViewInit {
  @Input() input: string;
  @Input() manualPopulate: boolean;
  @Input() hideActionBar: boolean;
  @Input() hideFilters: boolean;
  @Input() hideSelectors: boolean;
  @Input() pageSizeOverride: number;
  @Input() filtersOverride: MultiFilterForm;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(JobActionComponent) jobActionRef: JobActionComponent;
  @ViewChild(TableHeaderSelectorComponent) tableHeadSelectorRef: TableHeaderSelectorComponent;
  displayedColumns: string[] = [
    'job_id',
    'name',
    'priority',
    'created_time_sec_utc',
    'start_time_sec_utc',
    'finished_time_sec_utc',
    'job_status',
  ];
  jobSelectOptions: string[] = ['Visible'];
  jobs = new MatTableDataSource<Job>();

  loading = false;
  numJobs = 0;
  expandedElement: Job|null;
  startingPageSize: number;

  filters = new MultiFilterForm(FILTER_PARAMETERS);
  jobId: string = JOB_ID;
  jobName: string = JOB_NAME;
  jobPriority: string = JOB_PRIORITY;
  queueStatus: string = QUEUE_STATUS;
  jobRelationship: string = JOB_RELATIONSHIP;
  jobStartTimeFromFilter: string = JOB_START_TIME_FROM_FILTER;
  jobStartTimeToFilter: string = JOB_START_TIME_TO_FILTER;

  normalizeTimestamp = normalizeTimestamp;

  // Removing the first, default value of each enum ( which represent the 'unset'
  // state.
  relationshipFilterOptions = [''].concat(
    Object.keys(Job.Relationship).slice(1)
  );
  queueStatusFilterOptions = [''].concat(
    Object.keys(Job.QueueStatus).slice(1)
  );

  constructor(
    private readonly moblabGrpcService: MoblabGrpcService,
    private changeDetectorRefs: ChangeDetectorRef,
    private datePipe: DatePipe,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.applyFilters(params);
    });

    this.startingPageSize = this.pageSizeOverride ?
      this.pageSizeOverride : DEFAULT_PAGE_SIZE;

    if (this.paginator) {
      this.paginator.pageSize = this.startingPageSize;
    }

    if (this.filtersOverride) {
      this.filters = this.filtersOverride;
    }

    if (!this.hideSelectors) {
      this.displayedColumns = ['job_checkboxes'].concat(this.displayedColumns);
    }

    if (!this.manualPopulate) {
      this.moblabGrpcService.getNumJobs(
        (numJobs: number) => { this.numJobs = numJobs; }
      )
      this.getNextPageJobs();
    }
  }

  ngAfterViewInit() {
    this.paginator.page.subscribe(
      () => this.getNextPageJobs()
    );
  }

  applyFilters(params) {
    for (const filter_id of FILTER_PARAMETERS) {
      if (filter_id in params) {
        this.filters.getFormControl(filter_id).setValue(params[filter_id]);
      }
    }
  }

  selectionChanged(event) {
    if (event.selection === "All") {
      this.selectAllJobs();
    } else if (event.selection === "Visible") {
      this.jobs.data.forEach(this.jobActionRef.selectJob, this.jobActionRef);
    } else if (event.selection === "None") {
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
    const job_name_filter = this.filters.getFormValue(JOB_NAME);
    const job_start_lt_filter = datestringToSecondsTimestamp(
      this.filters.getFormValue(JOB_START_TIME_TO_FILTER)
    );
    const job_start_gt_filter = datestringToSecondsTimestamp(
      this.filters.getFormValue(JOB_START_TIME_FROM_FILTER)
    );
    const job_queue_status_filter = this.filters.getFormValue(QUEUE_STATUS) ?
      Number(Job.QueueStatus[this.filters.getFormValue(QUEUE_STATUS)]) : 0;
    const job_relationship_filter =
      this.filters.getFormValue(JOB_RELATIONSHIP) ?
        Number(Job.Relationship[this.filters.getFormValue(JOB_RELATIONSHIP)]) : 0;
    const parent_id_filter = this.filters.getFormValue(PARENT_JOB_ID);
    const dut_filter = this.filters.getFormValue(DUT_RUN_ON);
    return [job_id_filter, job_name_filter, job_start_lt_filter,
      job_start_gt_filter, job_queue_status_filter, job_relationship_filter,
      parent_id_filter, dut_filter]
  }

  selectJobIds(job_ids: number[]) {
    this.jobActionRef.selectJobs(job_ids);
    this.getNextPageJobs();
    this.jobs.filteredData.forEach(this.jobActionRef.selectJob, this.jobActionRef);
  }

  selectAllJobs() {
    /**
     * Queries backend for list of job ids that meet filter parameters and
     * selects all returned jobs in job action component.
     */
    this.loading = true;

    let [job_id_filter, job_name_filter, job_start_lt_filter,
      job_start_gt_filter, job_queue_status_filter, job_relationship_filter,
      parent_id_filter, dut_filter] = this.getJobFilters();

    this.moblabGrpcService.getJobIds(
      (job_ids: number[]) => {
        this.selectJobIds(job_ids)
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
      dut_filter,
    );
  }

  getPriorityFromNum(priorityNum) {
    return INT_TO_PRIORITY[priorityNum];
  }
  getStatusFromNum(statusNum) {
    return INT_TO_JOBSTATUS[statusNum];
  }

  assignJobs(jobs) {
    this.jobs = new MatTableDataSource(jobs);
    this.loading = false;
  }

  resetPagination() {
    if (this && this.paginator) {
      this.paginator.pageIndex = 0;
    }
  }

  filterSubmission() {
    this.resetPagination();
    this.getNextPageJobs()
  }

  clearFilters() {
    this.filters.reset();
  }

  refreshJobs(parentJobId?: string, dutRunOn?: string) {
    this.filters.setFormValue(PARENT_JOB_ID, parentJobId);
    this.filters.setFormValue(DUT_RUN_ON, dutRunOn);
    this.resetPagination();
    this.getNextPageJobs();
  }

  getNextPageJobs() {
    /**
     * Refreshes jobs table according to filter and paginator parameters.
     */
    this.loading = true;
    const [job_id_filter, job_name_filter, job_start_lt_filter,
      job_start_gt_filter, job_queue_status_filter, job_relationship_filter,
      parent_id_filter, dut_filter] = this.getJobFilters();

    this.moblabGrpcService.getJobs(
      (jobs: Job[]) => this.assignJobs(jobs),
      (message: string) => this.errorHandling(message),
      this.paginator && this.paginator.pageIndex ?
        this.paginator.pageIndex * this.paginator.pageSize : 0,
      this.paginator && this.paginator.pageSize ?
        this.paginator.pageSize : DEFAULT_PAGE_SIZE,
      job_id_filter,
      job_name_filter,
      job_start_lt_filter,
      job_start_gt_filter,
      job_queue_status_filter,
      job_relationship_filter,
      parent_id_filter,
      dut_filter,
    );

    this.moblabGrpcService.getNumJobs(
      (numJobs: number) => { this.numJobs = numJobs; },
      job_id_filter,
      job_name_filter,
      job_start_lt_filter,
      job_start_gt_filter,
      job_queue_status_filter,
      job_relationship_filter,
      parent_id_filter,
      dut_filter,
    )
  }

  getNumVisibleJobs() {
    return this.jobs.data.length;
  }

  getNumSelectedJobs() {
    return this.jobActionRef.getNumSelectedJobs();
  }

  /*
    Stops job detail expansion from happening when the user selects a job's
    checkbox.
  */
  checkboxClick(e) {
    e.stopPropagation();
  }

  errorHandling(message: string) {
    this.loading = false;
    this.setOffPopup(message);
  }

  isAllJobsSelected() {
    return this.jobActionRef.getNumSelectedJobs() === this.jobs.data.length;
  }

  ngOnDestroy(): void {
    this.paginator.page.unsubscribe();
  }

  setDutFilter(dut: string) {
    this.filters.setFormValue(DUT_RUN_ON, dut);
  }

  setOffPopup(dialogue) {
    const snackBarRef = this.snackBar.open(dialogue, '', {
      duration: 5000,
      verticalPosition: 'top',
      panelClass: ['action-submission-popup'],
    });
  }
}
