import {Component, Input, OnInit, ViewChild} from '@angular/core';
import {ConnectedDutInfo} from 'app/services/moblabrpc_pb';
import {MatSort, Sort} from '@angular/material/sort';
import {MatTableDataSource} from '@angular/material/table';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {SelectionModel} from '@angular/cdk/collections';

import {TableHeaderSelectorComponent} from
  '../../widgets/table-header-selector/table-header-selector.component';

const NOT_CONNECTED_MESSAGE = 'DUT not reachable by SSH';


@Component({
  selector: 'app-view-duts',
  templateUrl: './view-duts.component.html',
  styleUrls: ['./view-duts.component.css']
})
export class ViewDutsComponent implements OnInit {
  @Input() hideUnenrolledDuts = false;
  @ViewChild(TableHeaderSelectorComponent) headerSelectorRef: TableHeaderSelectorComponent;

  duts = new MatTableDataSource<ConnectedDutInfo>();
  displayedColumns: string[] = [
    'select',
    'name',
    'buildtarget',
    'model',
    'status',
    'pools',
  ];

  loading = false;

  selectOptions: string[] = ['All Enrolled', 'All Unenrolled'];


  filterLabels = true;

  selection = new SelectionModel<ConnectedDutInfo>(true, []);

  constructor(private moblabGrpcService: MoblabGrpcService) {}

  @ViewChild(MatSort, {}) sort: MatSort;

  sortingDataAccessor(item, property) {
    switch (property) {
      case 'name':
        return item.getName();
      case 'buildtarget':
        return item.getBuildTarget();
      case 'model':
        return item.getModel();
      case 'status':
        return item.getStatus();
    }
  }

  ngOnInit() {
    this.getConnectedDuts();
  }

  assignDuts(duts: ConnectedDutInfo[]) {
    this.duts = new MatTableDataSource<ConnectedDutInfo>(duts);
  }

  getConnectedDuts() {
    this.loading = true;
    this.moblabGrpcService.listConnectedDuts(
      (connectedDuts: ConnectedDutInfo[]) => {
        this.loading = false;
        this.assignDuts(connectedDuts);
      }
    );
  }

  getDisabledReason(dut: ConnectedDutInfo) {
    if (!dut.getIsConnected()) {
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
    if (event.selection == 'All') {
      this.duts.data.forEach(row => this.selection.select(row));
    } else if (event.selection == 'None') {
      this.selection.clear();
    } else if (event.selection == this.selectOptions[0]) {
      this.duts.data.filter(row => {
        if (row.getIsEnrolled()) {
          this.selection.select(row);
        } else {
          this.selection.deselect(row);
        }
      });
    } else if (event.selection == this.selectOptions[1]) {
      this.duts.data.filter(row => {
        if (!row.getIsEnrolled()) {
          this.selection.select(row);
        } else {
          this.selection.deselect(row);
        }
      });
    }
  }
}
