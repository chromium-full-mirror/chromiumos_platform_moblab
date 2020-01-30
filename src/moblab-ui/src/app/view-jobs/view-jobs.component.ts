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
} from '@angular/core';
import {DatePipe} from '@angular/common';
import {FormControl} from '@angular/forms';
import {MatTableDataSource} from '@angular/material';
import {SelectionModel} from '@angular/cdk/collections';
import {Job} from "app/services/moblabrpc_pb";
import {MoblabGrpcService} from '../services/moblab-grpc.service';

function createInvertedObj (obj) {
  const inverted_mappings = {};
  for (const key of Object.keys(obj)) {
    inverted_mappings[obj[key]] = key;
  }
  return inverted_mappings;
}

const INT_TO_JOBSTATUS = createInvertedObj(Job.JobStatus);
const INT_TO_PRIORITY = createInvertedObj(Job.Priority);

const JOB_NAME = 'name';
const JOB_ID = 'id';
const JOB_PRIORITY = 'priority';
const JOB_STATUS = 'jobStatus';
const JOB_START_TIME_FROM_FILTER = 'startTimeFromFilter';
const JOB_START_TIME_TO_FILTER = 'startTimeToFilter';
const FILTER_PARAMETERS = [
  JOB_NAME,
  JOB_ID,
  JOB_PRIORITY,
  JOB_STATUS,
  JOB_START_TIME_FROM_FILTER,
  JOB_START_TIME_TO_FILTER,
];

/*
  For handling multiple filter forms without having to repeat logic per
  FormControl.
*/
class MultiFilter {
  formControls = {};
  filterValues = {};
  subscriptions = {};

  constructor(private filterParameters: string[],
              private jobsRef: MatTableDataSource<Job>) {
    this.jobsRef = jobsRef;
    for (const filterName of filterParameters) {
      this.formControls[filterName] = new FormControl('');
      this.filterValues[filterName] = '';
      this.subscriptions[filterName] =
        this.formControls[filterName].valueChanges.subscribe(
        value => {
          this.filterValues[filterName] = value;
          this.jobsRef.filter = JSON.stringify(this.filterValues);
        }
      )
    }
  }

  getFormControl(filterName) {
    return this.formControls[filterName];
  }

  setJobsRef(jobsRef) {
    this.jobsRef = jobsRef;
  }

  reset() {
    for (const filterName in this.formControls) {
      this.formControls[filterName].setValue('');
    }
  }

  unsubscribeAll() {
    for (const filterName in this.subscriptions) {
      this.subscriptions[filterName].unsubscribe();
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
export class ViewJobsComponent implements OnInit, OnDestroy {
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

  expandedElement: Job|null;

  filters = new MultiFilter(FILTER_PARAMETERS, this.jobs);
  jobId: string = JOB_ID;
  jobName: string = JOB_NAME;
  jobPriority: string = JOB_PRIORITY;
  jobStatus: string = JOB_STATUS;
  jobStartTimeFromFilter: string = JOB_START_TIME_FROM_FILTER;
  jobStartTimeToFilter: string = JOB_START_TIME_TO_FILTER;

  priorityFilterOptions = [''].concat(Object.keys(Job.Priority));
  jobStatusFilterOptions = [''].concat(Object.keys(Job.JobStatus));

  filterFunction(data, filter) {
    const searchTerms = JSON.parse(filter);
    const startTimeFromFilterDate = new Date(searchTerms.startTimeFromFilter);
    const startTimeToFilterDate = new Date(searchTerms.startTimeToFilter);
    const jobStartTime = new Date(data.getStartTimeSecUtc());

    return data.getJobId().toString().indexOf(
        searchTerms.id.toLowerCase()) !== -1 &&
      data.getName().toLowerCase().indexOf(
        searchTerms.name.toLowerCase()) !== -1 &&
      INT_TO_PRIORITY[data.getPriority()].indexOf(
        searchTerms.priority) !== -1 &&
      INT_TO_JOBSTATUS[data.getStatus()].indexOf(
        searchTerms.jobStatus) !== -1 &&
      (
        isNaN(startTimeFromFilterDate.getTime()) ||
        jobStartTime >= startTimeFromFilterDate
      ) &&
      (
        isNaN(startTimeToFilterDate.getTime()) ||
        jobStartTime <= startTimeToFilterDate
      );
  }

  constructor(
    private readonly moblabGrpcService: MoblabGrpcService,
    private changeDetectorRefs: ChangeDetectorRef,
    private datePipe: DatePipe
  ) {}

  ngOnInit() {
    this.getJobsList();
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

  getStatusFromNum(statusNum) {
    return INT_TO_JOBSTATUS[statusNum];
  }

  getPriorityFromNum(priorityNum) {
    return INT_TO_PRIORITY[priorityNum];
  }

  assignJobs(jobs) {
    const data = this.jobs.data
      ? [...this.jobs.data, ...jobs]
      : jobs;
    this.jobs = new MatTableDataSource(data);
    this.filters.setJobsRef(this.jobs);
    this.jobs.filterPredicate = this.filterFunction;
    this.loadingJobs = false;
  }

  // Because timestamps may be returned in second, millisecond, or nanosecond
  // granularity, but Angular expects timestamps in milliseconds.
  normalizeTimestamp(timestamp) {
    if (timestamp === 0) {
      return 'N/A'
    }

    const digits_count = timestamp.toString().length
    if (digits_count === 10) {
      timestamp *= 1000
    } else if (digits_count === 16) {
      timestamp /= 1000
    }
    return this.datePipe.transform(new Date(timestamp), 'yyyy-MM-dd HH:mm:ss')
  }

  getNextPageJobs() {
    this.loadingJobs = true;
    this.moblabGrpcService.getJobs(
      (jobs: Job[]) => this.assignJobs(jobs)
    )};

  refreshJobsList() {
    this.jobs.data = [];
    this.getJobsList();
  }

  getJobsList() {
    this.loadingJobs = true;
    this.getNextPageJobs();
    this.filters.reset();
  }

  getNumJobs() {
    return this.jobs.data.length;
  }

  getNumVisibleJobs() {
    return this.jobs.filteredData.length;
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
    this.filters.unsubscribeAll();
  }
}
