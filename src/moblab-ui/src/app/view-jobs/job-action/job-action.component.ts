import {
  Component,
  EventEmitter,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import {Job} from 'app/services/moblabrpc_pb';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {SelectionModel} from '@angular/cdk/collections';
import {
  NotificationBannerComponent
} from 'app/widgets/notification-banner/notification-banner.component';

@Component({
  selector: 'app-job-action',
  templateUrl: './job-action.component.html',
  styleUrls: ['./job-action.component.css'],
})
export class JobActionComponent {
  @Output() actionSubmitted = new EventEmitter();

  actions = ['', 'Abort'];
  selectedAction = '';
  jobSelections = new SelectionModel<number>(true, []);
  numSelectedJobs = 0;

  constructor(
    private moblabGrpcService: MoblabGrpcService,
    private notificationBanner: NotificationBannerComponent,
  ) { }

  toggleJobSelection(element) {
    this.jobSelections.toggle(element.getJobId());
  }

  isSelected(element) {
    return (
      this.jobSelections.hasValue() &&
      this.jobSelections.isSelected(element.getJobId())
    );
  }

  selectJob(element) {
    this.jobSelections.select(element.getJobId());
  }

  selectJobs(jobs: number[]) {
    jobs.forEach(job_id => {
      this.jobSelections.select(job_id);
    });
  }

  clearSelectedJobs() {
    this.jobSelections.clear();
  }

  getNumSelectedJobs() {
    return this.jobSelections.selected.length;
  }

  doAction() {
    const jobIds = this.jobSelections.selected;

    if (this.selectedAction) {
      this.moblabGrpcService.abortJobs(
        resultMsg => {
          this.notificationBanner.notify(resultMsg);
        },
        errorMsg => {
          this.notificationBanner.error(errorMsg);
        },
        jobIds
      );
    }
    this.selectedAction = '';
    this.clearSelectedJobs();
    this.actionSubmitted.emit();
  }

  refresh() {
    this.clearSelectedJobs();
  }
}
