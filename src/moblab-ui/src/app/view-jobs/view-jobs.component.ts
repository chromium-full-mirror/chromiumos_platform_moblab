import {
  animate,
  state,
  style,
  transition,
  trigger,
} from '@angular/animations';
import {
  ChangeDetectorRef,
  Component,
  HostListener,
  OnDestroy,
  OnInit,
  AfterViewInit,
  AfterContentInit,
  ViewChild,
} from '@angular/core';
import {DatePipe} from '@angular/common';
import {FormControl} from '@angular/forms';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import {SelectionModel} from '@angular/cdk/collections';

import {Job} from 'app/services/moblabrpc_pb';
import {MoblabGrpcService} from '../services/moblab-grpc.service';
import { INT_TO_PRIORITY, INT_TO_JOBSTATUS } from '../utils/proto_helpers';
import { normalizeTimestamp, datestringToSecondsTimestamp } from '../utils/date';
import { forbiddenDateValidator, forbiddenIDValidator } from '../utils/validators';

const JOB_NAME = 'name';
const JOB_ID = 'id';
const JOB_PRIORITY = 'priority';
const QUEUE_STATUS = 'queueStatus';
const JOB_RELATIONSHIP = 'relationship';
const JOB_START_TIME_FROM_FILTER = 'startTimeFromFilter';
const JOB_START_TIME_TO_FILTER = 'startTimeToFilter';
const PARENT_JOB_ID = 'parent_job_id'
const FILTER_PARAMETERS = [
  JOB_NAME,
  JOB_ID,
  JOB_PRIORITY,
  QUEUE_STATUS,
  JOB_RELATIONSHIP,
  JOB_START_TIME_FROM_FILTER,
  JOB_START_TIME_TO_FILTER,
  PARENT_JOB_ID
];
const FILTER_VALIDATORS = {}

FILTER_VALIDATORS[JOB_START_TIME_FROM_FILTER] = [forbiddenDateValidator]
FILTER_VALIDATORS[JOB_START_TIME_TO_FILTER] = [forbiddenDateValidator]
FILTER_VALIDATORS[JOB_ID] = [forbiddenIDValidator]

const START_PAGE_SIZE = 25;

/*
  For handling multiple filter forms without having to repeat logic per
  FormControl.
*/
class MultiFilterForm {
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
  animations: [
    trigger('detailExpand', [
      state('collapsed', style({height: '0px', minHeight: '0px'})),
      state('expanded', style({height: '*', minHeight: '100px'})),
      transition(
        'expanded <=> collapsed',
        animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')
      ),
    ]),
  ],
  providers: [DatePipe]
})
export class ViewJobsComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild(MatPaginator, { static: false }) paginator: MatPaginator;
  displayedColumns: string[] = [
    'job_checkboxes',
    'job_id',
    'name',
    'priority',
    'created_time_sec_utc',
    'start_time_sec_utc',
    'finished_time_sec_utc',
    'job_status',
  ];
  jobSelectOptions: string[] = [];
  jobs = new MatTableDataSource<Job>();
  job_selections = new SelectionModel<Job>(true, []);
  loadingJobs = false;
  numJobs = 0;
  expandedElement: Job|null;

  filters = new MultiFilterForm(FILTER_PARAMETERS);
  jobId: string = JOB_ID;
  jobName: string = JOB_NAME;
  jobPriority: string = JOB_PRIORITY;
  queueStatus: string = QUEUE_STATUS;
  jobRelationship: string = JOB_RELATIONSHIP;
  jobStartTimeFromFilter: string = JOB_START_TIME_FROM_FILTER;
  jobStartTimeToFilter: string = JOB_START_TIME_TO_FILTER;

  normalizeTimestamp = normalizeTimestamp;

  pageSize: number = START_PAGE_SIZE;

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
  ) {}

  ngOnInit() {
    this.moblabGrpcService.getNumJobs(
      (numJobs: number) => { this.numJobs = numJobs; }
      )
    this.getNextPageJobs();
  }

  ngAfterViewInit() {
    this.paginator.page.subscribe(
      () => this.getNextPageJobs()
    );
  }
  selectJob(element) {
    this.job_selections.select(element);
  }

  selectionChanged(event) {
    if (event.selection === "All") {
      this.jobs.filteredData.forEach(this.selectJob, this);
    } else if (event.selection === "None") {
      this.job_selections.clear();
    }
  }

  getPriorityFromNum(priorityNum) {
    return INT_TO_PRIORITY[priorityNum];
  }
  getStatusFromNum(statusNum) {
    return INT_TO_JOBSTATUS[statusNum];
  }

  assignJobs(jobs) {
    this.jobs = new MatTableDataSource(jobs);
    this.loadingJobs = false;
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

  refreshJobs() {
    this.filters.reset();
    this.resetPagination();
    this.getNextPageJobs();
  }

  getNextPageJobs() {
    this.loadingJobs = true;

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

    this.moblabGrpcService.getJobs(
      (jobs: Job[]) => this.assignJobs(jobs),
      (this.paginator.pageIndex * this.paginator.pageSize) ?
        this.paginator.pageIndex * this.paginator.pageSize : 0,
      this.paginator.pageSize ?
        this.paginator.pageSize : this.pageSize,
      job_id_filter,
      job_name_filter,
      job_start_lt_filter,
      job_start_gt_filter,
      job_queue_status_filter,
      job_relationship_filter,
      parent_id_filter
    );

    this.moblabGrpcService.getNumJobs(
      (numJobs: number) => { this.numJobs = numJobs; },
      job_id_filter,
      job_name_filter,
      job_start_lt_filter,
      job_start_gt_filter,
      job_queue_status_filter,
      job_relationship_filter,
      parent_id_filter
    )
  }

  getNumVisibleJobs() {
    return this.jobs.data.length;
  }

  /*
    Stops job detail expansion from happening when the user selects a job's
    checkbox.
  */
  checkboxClick(e) {
    e.stopPropagation();
  }

  getNumSelectedJobs() {
    return this.job_selections.selected.length;
  }

  isAllJobsSelected() {
    const numSelected = this.getNumSelectedJobs();
    return numSelected === this.jobs.data.length;
  }

  ngOnDestroy(): void {
    this.paginator.page.unsubscribe();
  }
}
