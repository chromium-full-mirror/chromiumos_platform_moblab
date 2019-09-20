import {SelectionModel} from '@angular/cdk/collections';
import {Component, OnInit} from '@angular/core';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {ConnectedDutInfo} from 'app/services/moblabrpc_pb';

@Component({
  selector: 'app-enrollment',
  templateUrl: './enrollment.component.html',
  styleUrls: ['./enrollment.component.scss']
})
export class EnrollmentComponent implements OnInit {
  duts: ConnectedDutInfo[] = [];
  displayedColumns: string[] =
      ['select', 'name', 'board', 'model', 'status', 'labels'];

  labelFilterList: Set<string> = new Set();
  selectValue = 1;
  filterLabels = true;

  selection = new SelectionModel<ConnectedDutInfo>(true, []);

  constructor(private moblabGrpcService: MoblabGrpcService) {}

  ngOnInit() {
    this.selectValue = 1;
    this.getConnectedDuts();
  }

  getConnectedDuts() {
    this.moblabGrpcService.listConnectedDuts(
        (connectedDuts: ConnectedDutInfo[]) => {
          this.duts = connectedDuts;
          this.calculateLabelFilter();
          console.log(connectedDuts);
        });
  }

  toggleFilterLabels() {
    this.filterLabels = !this.filterLabels;
    this.calculateLabelFilter();
  }

  calculateLabelFilter() {
    this.labelFilterList.clear();
    if (this.filterLabels) {
      this.duts[0].getLabelsList().forEach(label => {
        this.labelFilterList.add(label);
      });

      // Remove board, model and pool labels
      this.labelFilterList.forEach(filter => {
        if (filter.startsWith('model:') || filter.startsWith('pool:') ||
            filter.startsWith('board:')) {
          this.labelFilterList.delete(filter);
        }
      });
    }
  }

  /**
   * Whether the number of selected elements matches the total number of rows.
   */
  isAllSelected() {
    const numSelected = this.selection.selected.length;
    const numRows = this.duts.length;
    return numSelected === numRows;
  }

  /**
   * Selects all rows if they are not all selected; otherwise clear selection.
   */
  masterToggle() {
    this.isAllSelected() ? this.selection.clear() :
                           this.duts.forEach(row => this.selection.select(row));
  }

  selectAllUnenrolled() {
    this.duts.filter(row => {
      if (!row.getIsEnrolled()) {
        this.selection.select(row);
      }
    });
  }

  enrollSelected() {
    const ips: string[] = [];
    this.duts.forEach(row => {
      if (this.selection.isSelected(row)) {
        ips.push(row.getIp());
      }
    });
    this.moblabGrpcService.enrollDuts(ips, () => {
      this.getConnectedDuts();
    });
  }

  unenrollSelected() {
    const ips: string[] = [];
    this.duts.forEach(row => {
      if (this.selection.isSelected(row)) {
        ips.push(row.getIp());
      }
    });
    this.moblabGrpcService.unenrollDuts(ips, () => {
      this.getConnectedDuts();
    });
  }
}
