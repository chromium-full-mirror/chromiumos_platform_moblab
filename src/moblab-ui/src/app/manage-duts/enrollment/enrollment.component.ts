import { SelectionModel } from "@angular/cdk/collections";
import { Component, OnInit, ViewChild } from "@angular/core";
import { MoblabGrpcService } from "app/services/moblab-grpc.service";
import { ConnectedDutInfo } from "app/services/moblabrpc_pb";
import { MatSort, Sort } from "@angular/material/sort";
import { MatTableDataSource } from "@angular/material/table";

@Component({
  selector: "app-enrollment",
  templateUrl: "./enrollment.component.html",
  styleUrls: ["./enrollment.component.scss"]
})
// class MyMatTableDataSource<T> extends MatTableDataSource<T> {}
export class EnrollmentComponent implements OnInit {
  duts = new MatTableDataSource<ConnectedDutInfo>();
  displayedColumns: string[] = [
    "select",
    "name",
    "buildtarget",
    "model",
    "status",
    "labels"
  ];

  selectOptions: string[] = ["All Enrolled", "All Unenrolled"];

  labelFilterList: Set<string> = new Set();

  filterLabels = true;

  selection = new SelectionModel<ConnectedDutInfo>(true, []);

  constructor(private moblabGrpcService: MoblabGrpcService) {}

  @ViewChild(MatSort, {}) sort: MatSort;

  sortingDataAccessor(item, property) {
    switch (property) {
      case "name":
        return item.getName();
      case "buildtarget":
        return item.getBuildTarget();
      case "model":
        return item.getModel();
      case "status":
        return item.getStatus();
    }
  }

  ngOnInit() {
    this.getConnectedDuts();
    this.duts.sortingDataAccessor = this.sortingDataAccessor;
    this.duts.sort = this.sort;
  }

  getConnectedDuts() {
    this.moblabGrpcService.listConnectedDuts(
      (connectedDuts: ConnectedDutInfo[]) => {
        this.duts.data = connectedDuts;
        this.calculateLabelFilter();
      }
    );
  }

  toggleFilterLabels() {
    this.filterLabels = !this.filterLabels;
    this.calculateLabelFilter();
  }

  calculateLabelFilter() {
    this.labelFilterList.clear();
    if (this.filterLabels) {
      this.duts.data[0].getLabelsList().forEach(label => {
        this.labelFilterList.add(label);
      });

      // Remove board, model and pool labels
      this.labelFilterList.forEach(filter => {
        if (
          filter.startsWith("model:") ||
          filter.startsWith("pool:") ||
          filter.startsWith("board:")
        ) {
          this.labelFilterList.delete(filter);
        }
      });
    }
  }

  enrollSelected() {
    const ips: string[] = [];
    this.duts.data.forEach(row => {
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
    this.duts.data.forEach(row => {
      if (this.selection.isSelected(row)) {
        ips.push(row.getIp());
      }
    });
    this.moblabGrpcService.unenrollDuts(ips, () => {
      this.getConnectedDuts();
    });
  }

  selectionChanged(event) {
    if (event.selection == "All") {
      this.duts.data.forEach(row => this.selection.select(row));
    } else if (event.selection == "None") {
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

  onSortChange(sortdetails: Sort) {
    console.log(this.sort);
    console.log(sortdetails);
  }
}
