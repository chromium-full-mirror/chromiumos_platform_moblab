import {Component, OnInit} from '@angular/core';
import {NewUpdateService} from '../../../services/new-update.service';
import {NewUpdateStatus} from '../../../constants';

@Component({
  selector: 'app-new-update-notifier',
  templateUrl: './new-update-notifier.component.html',
  styleUrls: ['./new-update-notifier.component.scss'],
})
export class NewUpdateNotifierComponent implements OnInit {
  showNotifier = false;
  updateStatus: number = NewUpdateStatus.UNKNOWN;

  constructor(private newUpdateService: NewUpdateService) {}

  ngOnInit(): void {
    // Subscribe to the Observable provided by NewUpdateService.
    this.newUpdateService.newUpdateStatusObservable.subscribe(data => {
      this.updateStatus = data['status'];
      this.showNotifier = this.isNewUpdateAvailable();
    });
  }

  isNewUpdateAvailable(): boolean {
    return (
      this.updateStatus === NewUpdateStatus.UPDATE_AVAILABLE ||
      this.updateStatus === NewUpdateStatus.UPDATE_AVAILABLE_WITH_JOBS_RUNNING
    );
  }
}
