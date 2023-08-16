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
import {NotificationsService} from '../services/notifications.service';
import {MoblabGrpcService} from '../services/moblab-grpc.service';
import {ViewJobsComponent} from '../view-jobs/view-jobs.component';

@Component({
  selector: 'app-dut-detail',
  templateUrl: './dut-detail.component.html',
  styleUrls: ['./dut-detail.component.scss'],
  animations: [],
})
export class DutDetailComponent implements OnInit, AfterContentInit {
  @ViewChild('dut_info_table') dutInfoTableRef: KeyValTableComponent;
  @ViewChild('dut_task_table') dutTaskTableRef: DutTaskTableComponent;
  @ViewChild('associated_jobs_table') associatedJobsTableRef: ViewJobsComponent;

  serverControlFile = '';
  dutQuery = new FormControl('', Validators.minLength(1));
  servoSerialNumber = new FormControl(
    '',
    Validators.pattern(
      '(SERVOV4P1-)?[CGS](-)?[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[0-1])[0-9]{4}'
    )
  );
  isDutInfoEmpty = true;

  constructor(
    private cd: ChangeDetectorRef,
    readonly moblabGrpcService: MoblabGrpcService,
    private route: ActivatedRoute,
    private notificationsService: NotificationsService
  ) {}

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
    this.isDutInfoEmpty = false;
    this.dutInfoTableRef.loadRows([
      ['DUT', dutInfo.getIp()],
      ['MAC', dutInfo.getMacAddr()],
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
    this.associatedJobsTableRef.setDutIp(this.dutQuery.value);
    this.associatedJobsTableRef.refreshJobs();
  }

  fetchDutDetails() {
    if (this.dutTaskTableRef) {
      this.dutTaskTableRef.setDutIp(this.dutQuery.value);
    }
    this.isDutInfoEmpty = true;

    this.moblabGrpcService.getDutDetails(
      (dutInfo: ConnectedDutInfo) => {
        this.setDutDetails(dutInfo);
      },
      errorMsg => {
        this.notificationsService.error(errorMsg);
      },
      this.dutQuery.value.trim()
    );
  }

  repairDut() {
    this.moblabGrpcService.repairDut(
      (message: string) => {
        this.notificationsService.notify(
          'Set off repair task on DUT, please refresh page for status.'
        );
      },
      errorMsg => {
        this.notificationsService.error(errorMsg);
      },
      this.dutQuery.value
    );
  }

  reverifyDut() {
    this.moblabGrpcService.reverifyDuts(
      (message: string) => {
        this.notificationsService.notify(
          'Set off reverify task on DUT, please refresh page for status.'
        );
      },
      errorMsg => {
        this.notificationsService.error(errorMsg);
      },
      [this.dutQuery.value]
    );
  }

  addServo() {
    this.moblabGrpcService.addServo(
      () => {
        this.notificationsService.notify(
          'Add servo serial number to dut and reverify, please refresh page for status.'
        );
      },
      errorMsg => {
        this.notificationsService.error(errorMsg);
      },
      this.dutQuery.value,
      this.servoSerialNumber.value
    );
  }
}
