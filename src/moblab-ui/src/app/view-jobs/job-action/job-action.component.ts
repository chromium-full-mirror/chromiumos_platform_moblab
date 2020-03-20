import {Component, EventEmitter, OnInit, Output, ViewChild} from '@angular/core';
import {Job} from 'app/services/moblabrpc_pb';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {SelectionModel} from '@angular/cdk/collections';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-job-action',
  templateUrl: './job-action.component.html',
  styleUrls: ['./job-action.component.css']
})

export class JobActionComponent {
  @Output() actionSubmitted = new EventEmitter();

  actions = ['', 'Abort'];
  selectedAction = '';
  jobSelections = new SelectionModel<Job>(true, []);
  numSelectedJobs = 0;

  constructor(private moblabGrpcService: MoblabGrpcService, private snackBar: MatSnackBar,) {}

  toggleJobSelection(element) {
    this.jobSelections.toggle(element);
  }

  isSelected(element) {
    return this.jobSelections.hasValue() && this.jobSelections.isSelected(element);
  }

  selectJob(element) {
    this.jobSelections.select(element);
  }

  clearSelectedJobs() {
    this.jobSelections.clear();
  }

  getNumSelectedJobs() {
    return this.jobSelections.selected.length;
  }

  doAction() {
    const jobIds = [];
      this.jobSelections.selected.forEach(
      (job) => {
        jobIds.push(job.getJobId());
      }
    );

    if (this.selectedAction) {
      this.moblabGrpcService.abortJobs(
        (msg) => {
          this.setOffPopup(msg)
        },
        (errorMsg) => {
          this.setOffPopup(errorMsg)
        },
        jobIds
      );
    }
    this.selectedAction = '';
    this.clearSelectedJobs();
    this.actionSubmitted.emit();
  }

  setOffPopup(message) {
    const snackBarRef = this.snackBar.open(message, '', {
      duration: 5000,
      verticalPosition: 'top',
      panelClass: ['action-submission-popup'],
    });
  }
}
