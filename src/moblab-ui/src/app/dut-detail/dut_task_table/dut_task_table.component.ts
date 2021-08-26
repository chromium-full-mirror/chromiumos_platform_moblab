import {AfterViewInit, Component, ViewChild} from '@angular/core';
import {MatPaginator} from '@angular/material/paginator';
import {MatTableDataSource} from '@angular/material/table';

import {DutTask} from '../../services/moblabrpc_pb';
import {INT_TO_DUT_TASK_STATUS} from '../../utils/proto_helpers';
import {MoblabGrpcService} from '../../services/moblab-grpc.service';
import {normalizeTimestamp} from '../../utils/date';
import {NotificationsService} from '../../services/notifications.service';
@Component({
  selector: 'app-dut-task-table',
  templateUrl: './dut_task_table.component.html',
  styleUrls: ['./dut_task_table.component.css'],
})
export class DutTaskTableComponent implements AfterViewInit {
  @ViewChild(MatPaginator) paginator: MatPaginator;

  displayedColumns: string[] = [
    'task',
    'time_started',
    'time_finished',
    'logs',
  ];

  dutIp: string;
  numDutTasks = 0;
  normalizeTimestamp = normalizeTimestamp;
  tasks = new MatTableDataSource<DutTask>();
  DEFAULT_PAGE_SIZE = 10;

  constructor(
    readonly moblabGrpcService: MoblabGrpcService,
    private notificationsService: NotificationsService
  ) {}

  ngAfterViewInit() {
    this.paginator.page.subscribe(() => this.getNextPageDutTasks());
  }

  setDutIp(dutIp: string) {
    this.dutIp = dutIp;
    this.getNextPageDutTasks();
  }

  setDutTasks(dut_tasks: DutTask[]) {
    this.tasks = new MatTableDataSource<DutTask>(dut_tasks);
  }

  getNextPageDutTasks() {
    this.moblabGrpcService.getDutTasks(
      (dutTasks: DutTask[]) => {
        this.setDutTasks(dutTasks);
      },
      errorMsg => {
        this.notificationsService.error(errorMsg);
      },
      this.dutIp,
      this.paginator.pageIndex * this.paginator.pageSize
        ? this.paginator.pageIndex * this.paginator.pageSize
        : 0,
      this.paginator.pageSize ? this.paginator.pageSize : this.DEFAULT_PAGE_SIZE
    );

    this.moblabGrpcService.getNumDutTasks(
      (numDutTasks: number) => {
        this.numDutTasks = numDutTasks;
      },
      errorMsg => {
        this.notificationsService.error(errorMsg);
      },
      this.dutIp
    );
  }

  getStatusFromNum(statusNum) {
    return INT_TO_DUT_TASK_STATUS[statusNum];
  }

  construct_task_logs_link(task: DutTask): string {
    return `/results/hosts/${this.dutIp}/${task.getTaskLogId().toLowerCase()}/`;
  }
}
