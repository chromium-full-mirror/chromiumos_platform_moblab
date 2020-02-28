import {Component, ViewChild} from '@angular/core';
import {MatExpansionPanel} from '@angular/material/expansion';
import {MatSnackBar} from '@angular/material/snack-bar';
import {MatTableDataSource} from '@angular/material/table';
import {FormControl, Validators} from '@angular/forms';

import {MoblabGrpcService} from '../services/moblab-grpc.service';
import {Job} from '../services/moblabrpc_pb';
import {normalizeTimestamp} from '../utils/date';
import {INT_TO_JOBSTATUS, INT_TO_PRIORITY} from '../utils/proto_helpers';
import {forbiddenIDValidator} from '../utils/validators';
import {ViewJobsComponent} from '../view-jobs/view-jobs.component';

interface KeyVal {
  key: string;
  value: string;
}

@Component({
  selector: 'app-job-detail',
  templateUrl: './job-detail.component.html',
  styleUrls: ['./job-detail.component.css'],
  animations: [],
  viewProviders: [MatExpansionPanel]
})
export class JobDetailComponent {
  @ViewChild(ViewJobsComponent) childViewJobsTableRef: ViewJobsComponent;
  jobQuery = new FormControl(
    '',
    [Validators.minLength(1), forbiddenIDValidator]
  );
  jobInfoTable = new MatTableDataSource<KeyVal>();
  jobHistoryTable = new MatTableDataSource<Job.Execution>();
  serverControlFile = '';

  normalizeTimestamp = normalizeTimestamp;

  jobDetailsTableColumns: string[] = ['key', 'value'];
  jobHistoryTableColumns: string[] = ['job_id', 'name', 'dut', 'start_time',
    'end_time', 'time_used', 'status'];

  constructor(
    private readonly moblabGrpcService: MoblabGrpcService,
    private snackBar: MatSnackBar
  ) {}

  getPriorityFromInt(enum_int) {
    return INT_TO_PRIORITY[enum_int]
  }

  getStatusFromInt(enum_int) {
    return INT_TO_JOBSTATUS[enum_int]
  }

  fetchJobDetails() {
    // Reset current job info.
    this.resetJob();
    this.childViewJobsTableRef.refreshJobs(this.jobQuery.value);

    this.moblabGrpcService.getJobDetails(
      (jobInfo: Job) => {
        this.unpackJobInfoToTable(jobInfo);
      },
      (errorMsg) => {
        this.reportError(errorMsg)
      },
      this.jobQuery.value
    )
  }

  unpackJobInfoToTable(job: Job) {
    const jobInfoRows: KeyVal[] = [];

    jobInfoRows.push({
      key: 'Name',
      value: job.getName()})
    jobInfoRows.push({
      key: 'ID',
      value: job.getJobId().toString()})
    jobInfoRows.push({
      key: 'Parent ID',
      value: job.getParentJobId().toString()})
    jobInfoRows.push({
      key: 'Dependencies',
      value: job.getDependencies()})
    jobInfoRows.push({
      key: 'Priority',
      value: INT_TO_PRIORITY[job.getPriority()]})
    jobInfoRows.push({
      key: 'Created time',
      value: normalizeTimestamp(job.getCreatedTimeSecUtc())})
    jobInfoRows.push({
      key: 'Status',
      value: INT_TO_JOBSTATUS[job.getStatus()]})
    jobInfoRows.push({
      key: 'Timeout',
      value: (job.getTimeout() / 60 / 1000).toString() + ' minutes'})
    jobInfoRows.push({
      key: 'Max Runtime',
      value: (job.getMaxRuntime() / 60 / 1000).toString() + ' minutes'})
    jobInfoRows.push({
      key: 'Test Retries',
      value: job.getTestRetries().toString()})

    this.jobInfoTable = new MatTableDataSource<KeyVal>(jobInfoRows);
    this.jobHistoryTable =
      new MatTableDataSource<Job.Execution>(job.getExecutionHistoryList());
    this.serverControlFile = job.getServerControlFile();
  }

  reportError(dialogue) {
    const snackBarRef = this.snackBar.open(dialogue, '', {
      duration: 5000,
      verticalPosition: 'top'
    });
    this.resetQuery();
  }

  resetJob() {
    this.jobInfoTable.data = [];
    this.jobHistoryTable.data = [];
  }

  resetQuery() {
    this.jobQuery.reset();
  }
}
