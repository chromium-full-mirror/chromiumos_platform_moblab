import {Component, OnInit, HostListener, ChangeDetectorRef} from '@angular/core';
import {MatSnackBar} from '@angular/material/snack-bar';
import {MatTableDataSource} from '@angular/material';
import {SelectionModel} from '@angular/cdk/collections';

import { Job } from "app/services/moblabrpc_pb";
import { MoblabGrpcService } from '../services/moblab-grpc.service';

function createInvertedObj (obj) {
  const inverted_mappings = {};
  for (const key of Object.keys(obj)) {
    inverted_mappings[obj[key]] = key;
  }
  return inverted_mappings;
}

@Component({
  selector: 'app-view-jobs',
  templateUrl: './view-jobs.component.html',
  styleUrls: ['./view-jobs.component.css'],
})
export class ViewJobsComponent implements OnInit {
  displayedColumns: string[] = ['job_checkboxes', 'job_id', 'name', 'priority', 'created_time_sec_utc', 'start_time_sec_utc', 'finished_time_sec_utc', 'job_status'];
  jobSelectOptions: string[] = [];
  jobs = new MatTableDataSource<Job>();
  job_selections = new SelectionModel<Job>(true, []);
  loadingJobs = false;
  constructor(private moblabGrpcService: MoblabGrpcService, private _snackBar: MatSnackBar, private ref: ChangeDetectorRef) {
  }

  ngOnInit() {
    this.getJobsList();

    // Proto enums do not have the reverse mappings (e.g., 2 : 'STARTED', in addition to 'STARTED' : 2.
    // This is problematic because job entries returned from rpc calls with status and priority
    // encoded as numbers rather than strings.
    // The two lines below modify the Job enums to have reverse mappings.
    Object.assign(Job.JobStatus, createInvertedObj(Job.JobStatus));
    Object.assign(Job.Priority, createInvertedObj(Job.Priority));
  }

  selectionChanged(event) {
    if (event.selection === "All") {
      this.jobs.data.forEach(this.selectJob, this);
    } else if (event.selection === "None") {
      this.job_selections.clear();
    }
  }

  getStatusFromNum(statusNum) {
    return Job.JobStatus[statusNum];
  }

  getPriorityFromNum(priorityNum) {
    return Job.Priority[priorityNum];
  }

  getNextPageJobs() {
    this.loadingJobs = true;
    this.moblabGrpcService.getJobs(
      (jobs: Job[]) => {
        // Appends returned jobs to existing jobs list, if jobs list already exists.
        const data: Job[] = this.jobs.data
          ? [...this.jobs.data, ...jobs]
          : jobs;
        this.jobs = new MatTableDataSource(data);
        this.loadingJobs = false;
      });
  }

  refreshJobsList() {
    this.jobs.data = [];
    this.getJobsList();
  }

  getJobsList() {
    this.loadingJobs = true;
    this.getNextPageJobs();
  }

  getNumJobs() {
    return this.jobs.data.length;
  }

  getNumSelectedJobs() {
    return this.job_selections.selected.length;
  }

  isAllJobsSelected() {
    const numSelected = this.getNumSelectedJobs();
    return numSelected === this.jobs.data.length;
  }

  selectJob(element) {
    this.job_selections.select(element);
  }
}
