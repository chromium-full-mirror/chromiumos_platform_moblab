import {ActivatedRoute} from '@angular/router';
import {Component, ViewChild} from '@angular/core';
import {FormControl, Validators} from '@angular/forms';
import {MatSnackBar} from '@angular/material/snack-bar';

import {ConnectedDutInfo} from '../services/moblabrpc_pb';
import {DutTaskTableComponent} from './dut_task_table/dut_task_table.component';
import {KeyValTableComponent} from '../widgets/keyval-table/keyval-table.component';
import {MoblabGrpcService} from '../services/moblab-grpc.service';
import {ViewJobsComponent} from '../view-jobs/view-jobs.component';


@Component({
  selector: 'app-dut-detail',
  templateUrl: './dut-detail.component.html',
  styleUrls: ['./dut-detail.component.css'],
  animations: [],
})
export class DutDetailComponent {
  @ViewChild(KeyValTableComponent) dutInfoTableRef: KeyValTableComponent;
  @ViewChild(DutTaskTableComponent) dutTaskTableRef: DutTaskTableComponent;
  @ViewChild(ViewJobsComponent) associatedJobsTableRef: ViewJobsComponent;

  serverControlFile = '';
  dutQuery = new FormControl(
    '',
    [Validators.minLength(1)]
  );

  constructor(
    private readonly moblabGrpcService: MoblabGrpcService,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.dutQuery.setValue(params.get('dut_hostname'));
      if (this.dutQuery.value) {
        this.fetchDutDetails();
      }
    });
  }

  setDutDetails(dutInfo: ConnectedDutInfo) {
    this.dutInfoTableRef.loadRows(
      [
        ['DUT', dutInfo.getIp()],
        ['Name', dutInfo.getName()],
        ['Status', dutInfo.getStatus()],
        ['Labels', dutInfo.getLabelsList().toString()],
        ['Current Job', dutInfo.getCurrentJob() ? dutInfo.getCurrentJob().toString() : ''],
        ['Current DUT Task', dutInfo.getCurrentDutTask()],
      ]
    )
  }

  fetchDutDetails() {
    this.dutTaskTableRef.setDutIp(this.dutQuery.value);
    this.moblabGrpcService.getDutDetails(
      (dutInfo: ConnectedDutInfo) => {
        this.setDutDetails(dutInfo);
      },
      (errorMsg) => {
        this.setOffPopup(errorMsg)
      },
      this.dutQuery.value
    );

    this.associatedJobsTableRef.refreshJobs(undefined, this.dutQuery.value);
  }

  repairDut() {
    this.moblabGrpcService.repairDut((message: string) => {
        this.setOffPopup('Set off repair task on DUT, please refresh page for status.')
      },
      (errorMsg) => {
        this.setOffPopup(errorMsg)
      },
      this.dutQuery.value
    );
  }

  reverifyDut() {
    this.moblabGrpcService.reverifyDut((message: string) => {
        this.setOffPopup('Set off reverify task on DUT, please refresh page for status.')
      },
      (errorMsg) => {
        this.setOffPopup(errorMsg)
      },
      this.dutQuery.value
    );
  }

  setOffPopup(dialogue) {
    const snackBarRef = this.snackBar.open(dialogue, '', {
      duration: 5000,
      verticalPosition: 'top'
    });
  }

  isDutInfoTableEmpty() {
    return !this.dutInfoTableRef || this.dutInfoTableRef.isEmpty();
  }
}
