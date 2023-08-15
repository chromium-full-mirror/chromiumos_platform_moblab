import {ActivatedRoute} from '@angular/router';
import {
  AfterContentInit,
  Component,
  Input,
  OnInit,
  ViewChild,
} from '@angular/core';
import {ChangeDetectorRef} from '@angular/core';
import {MatExpansionPanel} from '@angular/material/expansion';
import {MatTableDataSource} from '@angular/material/table';
import {FormControl, Validators} from '@angular/forms';

import {MoblabGrpcService} from '../services/moblab-grpc.service';
import {Job, Execution} from '../services/moblabrpc_pb';
import {normalizeTimestamp} from '../utils/date';
import {INT_TO_JOBSTATUS, INT_TO_PRIORITY} from '../utils/proto_helpers';
import {forbiddenIDValidator} from '../utils/validators';
import {ViewJobsComponent} from '../view-jobs/view-jobs.component';
import {
  KeyVal,
  KeyValTableComponent,
} from '../widgets/keyval-table/keyval-table.component';
import {NotificationsService} from '../services/notifications.service';

import JobStatus = Job.JobStatus;

@Component({
  selector: 'app-job-detail',
  templateUrl: './job-detail.component.html',
  styleUrls: ['./job-detail.component.scss'],
  animations: [],
  viewProviders: [MatExpansionPanel],
})
export class JobDetailComponent implements OnInit, AfterContentInit {
  @ViewChild('child_view_jobs_table') childViewJobsTableRef: ViewJobsComponent;
  @ViewChild('job_info_table') jobInfoTableRef: KeyValTableComponent;
  jobQuery = new FormControl('', [
    Validators.minLength(1),
    forbiddenIDValidator,
  ]);
  jobInfoTable = new MatTableDataSource<KeyVal>();
  jobHistoryTable = new MatTableDataSource<Execution>();
  associatedDutsTable = new MatTableDataSource<Execution>();
  serverControlFile = '';

  normalizeTimestamp = normalizeTimestamp;

  jobDetailsTableColumns: string[] = ['key', 'value'];
  jobHistoryTableColumns: string[] = [
    'job_id',
    'name',
    'dut',
    'start_time',
    'end_time',
    'time_used',
    'status',
  ];
  associatedDutsTableColumns: string[] = [
    'dut',
    'dut_status',
    'status',
    'logs',
  ];

  constructor(
    private cd: ChangeDetectorRef,
    private readonly moblabGrpcService: MoblabGrpcService,
    private route: ActivatedRoute,
    private notificationsService: NotificationsService
  ) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.jobQuery.setValue(params.get('job_id'));
    });
  }

  ngAfterContentInit(): void {
    if (this.jobQuery.value) {
      this.fetchJobDetails();
    }
    this.cd.detectChanges();
  }

  getPriorityFromInt(enum_int) {
    return INT_TO_PRIORITY[enum_int];
  }

  getStatusFromInt(enum_int) {
    return INT_TO_JOBSTATUS[enum_int];
  }

  fetchJobDetails() {
    // Reset current job info.
    this.resetJob();

    this.moblabGrpcService.getJobDetails(
      (jobInfo: Job) => {
        this.unpackJobInfoToTable(jobInfo);
      },
      errorMsg => {
        this.notificationsService.error(errorMsg);
      },
      this.jobQuery.value
    );
  }

  unpackJobInfoToTable(job: Job) {
    this.jobInfoTableRef.loadRows([
      ['Name', job.getName()],
      ['ID', job.getJobId().toString()],
      ['Parent ID', job.getParentJobId().toString()],
      ['Dependencies', job.getDependencies()],
      ['Priority', INT_TO_PRIORITY[job.getPriority()]],
      ['Created time', normalizeTimestamp(job.getCreatedTimeSecUtc())],
      ['Status', INT_TO_JOBSTATUS[job.getStatus()]],
      ['Timeout', (job.getTimeout() / 60 / 1000).toString() + ' minutes'],
      [
        'Max Runtime',
        (job.getMaxRuntime() / 60 / 1000).toString() + ' minutes',
      ],
    ]);

    this.jobHistoryTable = new MatTableDataSource<Execution>(
      job.getExecutionHistoryList()
    );
    this.associatedDutsTable = new MatTableDataSource<Execution>(
      job.getAssociatedDutsList()
    );
    this.serverControlFile = job.getServerControlFile();
    this.childViewJobsTableRef.setParentJobId(this.jobQuery.value);
    this.childViewJobsTableRef.refreshJobs();
  }

  getLogsLink(execution: Execution) {
    const link = `/results/${execution.getJobId()}-moblab/${execution.getDut()}/`;
    return link;
  }

  resetJob() {
    this.jobInfoTable.data = [];
    this.jobHistoryTable.data = [];
  }

  resetQuery() {
    this.jobQuery.reset();
  }

  isJobInfoTableEmpty() {
    return !this.jobInfoTableRef || this.jobInfoTableRef.isEmpty();
  }

  isJobQueryEmpty() {
    return !this.jobInfoTableRef || !this.jobQuery.value;
  }
}
