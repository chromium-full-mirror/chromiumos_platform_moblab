import {Component, OnInit} from '@angular/core';
import {MatDialogRef} from '@angular/material/dialog';
import {NewUpdateService as GlobalNewUpdateService} from '../../../services/new-update.service';
import {NewUpdateStatus} from '../../../constants';

const data = {
  [NewUpdateStatus.UNKNOWN]: {
    title: 'An error occurred',
    blurb: [
      'Could not determine if the Moblab has new updates available due to error:',
    ],
    cancelLabel: 'DISMISS',
    sendLabel: 'HIDE THIS',
    showCancelLabelOnly: true,
  },
  [NewUpdateStatus.NO_UPDATE]: {
    title: 'Moblab is up to date.',
    blurb: ['No action is required at this time.'],
    cancelLabel: 'DISMISS',
    sendLabel: 'HIDE THIS',
    showCancelLabelOnly: true,
  },
  [NewUpdateStatus.UPDATE_AVAILABLE]: {
    title: 'A new update is available!',
    blurb: [
      "There's a new update available for your Moblab.",
      `To install the update, you will need to "Pause" the Job Scheduler,
      and then click on the "Update" button on the About Page.`,
    ],
    cancelLabel: 'NOT NOW',
    sendLabel: 'GO TO THE ABOUT PAGE',
    showCancelLabelOnly: false,
  },
  [NewUpdateStatus.UPDATE_AVAILABLE_WITH_JOBS_RUNNING]: {
    title: 'A new update is available!',
    blurb: [
      `There's a new update available for your Moblab but it can only
      be installed once all the running jobs are done.`,
      `To install the update, you will need to "Pause" the Job Scheduler,
      wait for all running jobs to finish, and then click on the
      "Update" button on the About Page.`,
    ],
    cancelLabel: 'NOT NOW',
    sendLabel: 'GO TO THE ABOUT PAGE',
    showCancelLabelOnly: false,
  },
};

@Component({
  selector: 'new-update-dialog',
  templateUrl: './new-update-dialog.component.html',
  styleUrls: ['./new-update-dialog.component.scss'],
})
export class NewUpdateDialogComponent implements OnInit {
  public showToolbar = false;
  private updateStatus: number = NewUpdateStatus.UNKNOWN;
  public title: string = data[this.updateStatus].title;
  public blurb: Array<string> = data[this.updateStatus].blurb;
  public cancelLabel: string = data[this.updateStatus].cancelLabel;
  public sendLabel: string = data[this.updateStatus].sendLabel;
  public showCancelLabelOnly: boolean =
    data[this.updateStatus].showCancelLabelOnly;
  private error = `This error message should never show on screen.
                          If it does, please report feedback with detailing
                          this error message.`;

  constructor(
    public dialogRef: MatDialogRef<NewUpdateDialogComponent>,
    private globalNewUpdateService: GlobalNewUpdateService
  ) {}

  ngOnInit() {
    // Subscribe to the NewUpdateStatusObservable.
    this.globalNewUpdateService.newUpdateStatusObservable.subscribe(obsData => {
      this.updateStatus = obsData['status'];
      this.error = obsData['reason'];
      this.title = data[this.updateStatus]['title'];
      // Make a copy of the array because you'll keep appending to the same
      // instance of the Array causing the output of blurb to become weirder
      // and weirder.
      this.blurb = Object.assign([], data[this.updateStatus]['blurb']);
      // Append error if any.
      if (this.error !== '') {
        this.blurb.push(this.error);
      }
      this.cancelLabel = data[this.updateStatus]['cancelLabel'];
      this.sendLabel = data[this.updateStatus]['sendLabel'];
      this.showCancelLabelOnly = data[this.updateStatus]['showCancelLabelOnly'];
    });
  }
}
