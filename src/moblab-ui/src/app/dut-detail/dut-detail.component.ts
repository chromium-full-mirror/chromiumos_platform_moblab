import {ActivatedRoute} from '@angular/router';
import {
  AfterContentInit,
  ChangeDetectorRef,
  Component,
  OnInit,
  ViewChild,
} from '@angular/core';
import {FormControl, Validators} from '@angular/forms';

import {ConnectedDutInfo} from '../services/moblabrpc_pb';
import {INT_TO_DUT_STATUS} from '../utils/proto_helpers';
import {DutTaskTableComponent} from './dut_task_table/dut_task_table.component';
import {KeyValTableComponent} from '../widgets/keyval-table/keyval-table.component';
import {
  NotificationBannerComponent
} from 'app/widgets/notification-banner/notification-banner.component';
import {MoblabGrpcService} from '../services/moblab-grpc.service';
import {ViewJobsComponent} from '../view-jobs/view-jobs.component';

@Component({
  selector: 'app-dut-detail',
  templateUrl: './dut-detail.component.html',
  styleUrls: ['./dut-detail.component.css'],
  animations: [],
})
export class DutDetailComponent implements OnInit, AfterContentInit {
  @ViewChild('dut_info_table') dutInfoTableRef: KeyValTableComponent;
  @ViewChild('dut_task_table') dutTaskTableRef: DutTaskTableComponent;
  @ViewChild('associated_jobs_table') associatedJobsTableRef: ViewJobsComponent;

  serverControlFile = '';
  dutQuery = new FormControl('', [Validators.minLength(1)]);

  constructor(
    private cd: ChangeDetectorRef,
    readonly moblabGrpcService: MoblabGrpcService,
    private route: ActivatedRoute,
    private notificationBanner: NotificationBannerComponent,
  ) { }

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.dutQuery.setValue(params.get('dut_hostname'));
    });
  }

  ngAfterContentInit() {
    if (this.dutQuery.value) {
      this.fetchDutDetails();
    }
    this.cd.detectChanges();
  }

  setDutDetails(dutInfo: ConnectedDutInfo) {
    this.dutInfoTableRef.loadRows([
      ['DUT', dutInfo.getIp()],
      ['MAC', dutInfo.getMacAddr()],
      ['Name', dutInfo.getName()],
      ['Status', INT_TO_DUT_STATUS[dutInfo.getStatus()]],
      ['Labels', dutInfo.getLabelsList().toString()],
      ['Attributes', dutInfo.getAttributesList().toString()],
      [
        'Current Job',
        dutInfo.getCurrentJob() ? dutInfo.getCurrentJob().toString() : '',
      ],
      ['Current DUT Task', dutInfo.getCurrentDutTask()],
    ]);
    this.dutTaskTableRef.setDutIp(this.dutQuery.value);
    this.associatedJobsTableRef.refreshJobs(undefined, this.dutQuery.value);
  }

  fetchDutDetails() {
    if (this.dutTaskTableRef) {
      this.dutTaskTableRef.setDutIp(this.dutQuery.value);
    }

    this.moblabGrpcService.getDutDetails(
      (dutInfo: ConnectedDutInfo) => {
        this.setDutDetails(dutInfo);
      },
      errorMsg => {
        this.notificationBanner.error(errorMsg);
      },
      this.dutQuery.value
    );
  }

  repairDut() {
    this.moblabGrpcService.repairDut(
      (message: string) => {
        this.notificationBanner.notify(
          'Set off repair task on DUT, please refresh page for status.'
        );
      },
      errorMsg => {
        this.notificationBanner.error(errorMsg);
      },
      this.dutQuery.value
    );
  }

  reverifyDut() {
    this.moblabGrpcService.reverifyDuts(
      (message: string) => {
        this.notificationBanner.notify(
          'Set off reverify task on DUT, please refresh page for status.'
        );
      },
      errorMsg => {
        this.notificationBanner.error(errorMsg);
      },
      [this.dutQuery.value]
    );
  }

  isDutInfoTableEmpty() {
    return !this.dutInfoTableRef || this.dutInfoTableRef.isEmpty();
  }
}
