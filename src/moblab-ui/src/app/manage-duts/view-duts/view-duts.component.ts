import {
  Component,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { MatDialog } from '@angular/material/dialog';
import { SelectionModel } from '@angular/cdk/collections';
import { ConnectedDutInfo } from 'app/services/moblabrpc_pb';
import { MoblabGrpcService } from 'app/services/moblab-grpc.service';
import { NotificationsService } from 'app/services/notifications.service';
import { BuildTargetAccessService } from 'app/services/build-target-access.service';
import { StageBuildDialogComponent } from '../stage-build-dialog/stage-build-dialog.component';

import { INT_TO_DUT_STATUS } from '../../utils/proto_helpers';
import { TableHeaderSelectorComponent } from '../../widgets/table-header-selector/table-header-selector.component';
import { Subscription, distinctUntilChanged, map } from 'rxjs';

const NOT_CONNECTED_MESSAGE = 'DUT not reachable by SSH';
const NO_ACCESS_MESSAGE =
  'The account does not have access to this build target';
const ALL_ENROLLED = 'All Enrolled';
const ALL_UNENROLLED = 'All Unenrolled';
const REPAIR_FAILED = 'Repair Failed';

@Component({
  selector: 'app-view-duts',
  templateUrl: './view-duts.component.html',
  styleUrls: ['./view-duts.component.scss'],
})
export class ViewDutsComponent implements OnInit, OnDestroy {
  @Input() hideEnrolledDuts = false;
  @Input() hideUnenrolledDuts = false;
  // The event emitter wants to notfiy the parent
  // component has been changed
  @Output() selectedDUTsChanged: EventEmitter<void> = new EventEmitter();
  @ViewChild(TableHeaderSelectorComponent)
  headerSelectorRef: TableHeaderSelectorComponent;

  duts = new MatTableDataSource<ConnectedDutInfo>();
  displayedColumns: string[] = [
    'select',
    'ip',
    'mac',
    'buildtarget',
    'model',
    'status',
    'pools',
    'labels',
  ];

  loading = false;

  // Create a local copy as we need to use it in view-duts.component.html.
  intToDutStatus = INT_TO_DUT_STATUS;

  filterLabels = true;

  selection = new SelectionModel<ConnectedDutInfo>(true, []);
  buildTargets: string[] = [];

  public selectOptions: string[] = [];

  @ViewChild(MatSort, {}) matSort: MatSort;

  // The subscriptions that we need to dispose after
  // the component destory.
  private disposers: Subscription[] = [];

  constructor(
    public moblabGrpcService: MoblabGrpcService,
    public dialog: MatDialog,
    private notificationsService: NotificationsService,
    private buildTargetAccessService: BuildTargetAccessService
  ) {}

  sortingDataAccessor(item, property) {
    switch (property) {
      case 'ip':
        return item.getIp();
      case 'mac':
        return item.getMacAddr();
      case 'buildtarget':
        return item.getBuildTarget();
      case 'model':
        return item.getModel();
      case 'status':
        return item.getStatus();
    }
  }

  ngOnInit() {
    this.setupSelectOptions();
    this.getConnectedDuts();
    this.buildTargetAccessService.buildTargetsObservable.subscribe(
      buildTargets => {
        this.buildTargets = buildTargets;
      }
    );
    this.disposers.push(
      this.selection.changed
        .pipe(
          map(e => e.source.selected.length),
          distinctUntilChanged()
        )
        .subscribe(_ => {
          this.selectedDUTsChanged.emit();
        })
    );
  }

  ngOnDestroy(): void {
    this.disposers.forEach(e => e.unsubscribe());
  }

  ngOnChanges(changes: any) {
    if (changes.hideUnenrolledDuts || changes.hideEnrolledDuts) {
      this.setupSelectOptions();
    }
  }

  private setupSelectOptions() {
    this.selectOptions = [
      ...(this.hideEnrolledDuts ? [] : [ALL_ENROLLED]),
      ...(this.hideUnenrolledDuts ? [] : [ALL_UNENROLLED]),
      REPAIR_FAILED,
    ];
  }

  assignDuts(duts: ConnectedDutInfo[]) {
    this.duts = new MatTableDataSource<ConnectedDutInfo>(duts);
    this.duts.sortingDataAccessor = this.sortingDataAccessor;
    this.duts.sort = this.matSort;
  }

  getConnectedDuts() {
    this.loading = true;
    this.moblabGrpcService.listConnectedDuts(
      (connectedDuts: ConnectedDutInfo[]) => {
        this.loading = false;
        this.buildTargetAccessService.updateModelsWithoutAccess(connectedDuts);
        this.assignDuts(connectedDuts);
        this.unselectAll();
      },
      (message: string) => {
        this.loading = false;
        this.assignDuts([]);
        this.unselectAll();
        this.notificationsService.error(message);
      }
    );
  }

  hasAccessToBuildTarget(dut: ConnectedDutInfo) {
    // skip the access check if dut is not enrolled or API has not returned yet
    if (this.buildTargets.length === 0 || !dut.getIsEnrolled()) {
      return true;
    }
    return this.buildTargets.includes(dut.getBuildTarget());
  }

  getDisabledReason(dut: ConnectedDutInfo) {
    if (!this.hasAccessToBuildTarget(dut)) {
      return NO_ACCESS_MESSAGE;
    } else if (!dut.getIsConnected()) {
      return NOT_CONNECTED_MESSAGE;
    } else {
      return '';
    }
  }

  setHideUnenrolledDuts(hide: boolean) {
    this.hideUnenrolledDuts = hide;
  }

  getNumSelectedDuts() {
    return this.selection.selected.length;
  }

  refreshConnectedDuts() {
    this.duts.data = [];
    this.getConnectedDuts();
  }

  startLoadingSpinner() {
    this.loading = true;
  }

  stopLoadingSpinner() {
    this.loading = false;
  }

  toggleFilterLabels() {
    this.filterLabels = !this.filterLabels;
  }

  getSelectedDutHostnames() {
    const hostnames: string[] = [];
    this.duts.data.forEach(row => {
      if (this.selection.isSelected(row)) {
        hostnames.push(row.getIp());
      }
    });
    return hostnames;
  }

  unselectAll() {
    this.headerSelectorRef.setCheckboxState(false);
    this.selection.clear();
  }

  selectionChanged(event) {
    if (event.selection === 'All') {
      this.duts.data
        .filter(e => {
          return (
            e.getIsConnected() &&
            (this.hideUnenrolledDuts ? e.getIsEnrolled() : true)
          );
        })
        .forEach(row => this.selection.select(row));
    } else if (event.selection === 'None') {
      this.selection.clear();
    } else if (event.selection === ALL_ENROLLED) {
      this.duts.data.filter(row => {
        if (row.getIsEnrolled() && row.getIsConnected()) {
          this.selection.select(row);
        } else {
          this.selection.deselect(row);
        }
      });
    } else if (!this.hideUnenrolledDuts && event.selection === ALL_UNENROLLED) {
      this.duts.data.filter(row => {
        if (!row.getIsEnrolled() && row.getIsConnected()) {
          this.selection.select(row);
        } else {
          this.selection.deselect(row);
        }
      });
    } else if (event.selection === REPAIR_FAILED) {
      this.duts.data.filter(row => {
        if (
          row.getStatus() ===
          ConnectedDutInfo.DutStatus.DUT_STATUS_REPAIR_FAILED &&
          row.getIsConnected()
        ) {
          this.selection.select(row);
        } else {
          this.selection.deselect(row);
        }
      });
    }
  }

  async accessTestBuild() {
    const dialogRef = this.dialog.open(StageBuildDialogComponent);
    try {
      const responseMessage = await dialogRef.afterClosed().toPromise();
      if (responseMessage) {
        this.notificationsService.notify(responseMessage);
      }
    } catch (error) {
      if (typeof error === 'string') {
        this.notificationsService.error(error);
      }
    }
  }
}
