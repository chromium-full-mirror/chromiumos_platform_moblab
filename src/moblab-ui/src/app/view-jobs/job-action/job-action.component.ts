import {Component, EventEmitter, Output} from '@angular/core';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {SelectionModel} from '@angular/cdk/collections';
import {NotificationsService} from 'app/services/notifications.service';

@Component({
  selector: 'app-job-action',
  templateUrl: './job-action.component.html',
  styleUrls: ['./job-action.component.css'],
})
export class JobActionComponent {
  @Output() actionSubmitted = new EventEmitter();

  jobSelections = new SelectionModel<number>(true, []);
  numSelectedJobs = 0;

  constructor(
    private moblabGrpcService: MoblabGrpcService,
    private notificationsService: NotificationsService
  ) {}

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
    this.moblabGrpcService.abortJobs(
      resultMsg => {
        this.notificationsService.notify(resultMsg);
      },
      errorMsg => {
        this.notificationsService.error(errorMsg);
      },
      jobIds
    );
    this.clearSelectedJobs();
    this.actionSubmitted.emit();
  }

  refresh() {
    this.clearSelectedJobs();
  }
}
