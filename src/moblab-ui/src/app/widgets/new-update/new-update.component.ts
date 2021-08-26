import {Component, OnInit} from '@angular/core';
import {NewUpdateService} from '../../services/new-update.service';
import {NewUpdateStatus} from '../../constants';

const mappings = {
  [NewUpdateStatus.UNKNOWN]: {
    icon: 'update_disabled',
    color: 'orange',
    tooltip: 'Error while detemining update availability',
  },
  [NewUpdateStatus.NO_UPDATE]: {
    icon: 'check_circle',
    color: 'green',
    tooltip: 'Moblab is updated',
  },
  [NewUpdateStatus.UPDATE_AVAILABLE]: {
    icon: 'update',
    color: 'yellow',
    tooltip: 'An update is available',
  },
  [NewUpdateStatus.UPDATE_AVAILABLE_WITH_JOBS_RUNNING]: {
    icon: 'update',
    color: 'orange',
    tooltip: 'An update is available but Jobs are currently running',
  },
};

@Component({
  selector: 'app-new-update',
  template: `
    <mat-icon
      class="feedback-icon new-update-cursor {{ colorClass }}"
      [matTooltip]="tooltip"
      new-update
      >{{ icon }}</mat-icon
    >
  `,
  styleUrls: ['./new-update.component.css'],
})
export class NewUpdateComponent implements OnInit {
  icon: string;
  tooltip: string;
  colorClass: string;

  constructor(private newUpdateService: NewUpdateService) {}

  ngOnInit(): void {
    // Subscribe to the Observable provided by NewUpdateService.
    this.newUpdateService.newUpdateStatusObservable.subscribe(data => {
      this.icon = mappings[data['status']].icon;
      this.colorClass = mappings[data['status']].color;
      this.tooltip = mappings[data['status']].tooltip;
    });
  }
}
