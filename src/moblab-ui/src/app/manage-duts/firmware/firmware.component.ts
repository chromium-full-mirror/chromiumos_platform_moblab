import {SelectionModel} from '@angular/cdk/collections';
import {Component, OnInit, Inject} from '@angular/core';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {
  ConnectedDutFirmwareInfo,
  FirmwareUpdateCommandOutput,
} from 'app/services/moblabrpc_pb';
import {MatDialog, MAT_DIALOG_DATA} from '@angular/material/dialog';

@Component({
  selector: 'app-firmware',
  templateUrl: './firmware.component.html',
  styleUrls: ['./firmware.component.scss'],
})
export class FirmwareComponent implements OnInit {
  firmware_duts = [];
  firmwareDisplayedColumns: string[] = [
    'select',
    'name',
    'current_firmware',
    'updater_firmware',
  ];
  loading = false;

  selection = new SelectionModel<ConnectedDutFirmwareInfo>(true, []);

  constructor(
    private moblabGrpcService: MoblabGrpcService,
    public dialog: MatDialog
  ) {}

  ngOnInit() {
    this.getConnectedDutsFirmware();
  }

  getConnectedDutsFirmware() {
    this.loading = true;
    this.moblabGrpcService.listConnectedDutsFirmware(
      (connectedDutsFirmware: ConnectedDutFirmwareInfo[]) => {
        this.firmware_duts = connectedDutsFirmware;
        this.loading = false;
      }
    );
  }

  updateFirmware() {
    const dialogRef = this.dialog.open(FirmwareUpdateConfirmDialog);

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loading = true;
        const ips: string[] = [];
        this.firmware_duts.forEach(row => {
          if (this.selection.isSelected(row)) {
            ips.push(row.getIp());
          }
        });
        this.moblabGrpcService.updateFirmwareOnDuts(
          ips,
          (results: FirmwareUpdateCommandOutput[]) => {
            this.loading = false;
            const dialogRef = this.dialog.open(FirmwareUpdateResultDialog, {
              data: results,
            });
            dialogRef.afterClosed().subscribe(result => {
              this.getConnectedDutsFirmware();
            });
          }
        );
      }
    });
  }

  selectionChanged(event: {selection: string}) {
    if (event.selection === 'All') {
      this.firmware_duts.forEach(row => this.selection.select(row));
    } else if (event.selection === 'None') {
      this.selection.clear();
    }
  }
}

@Component({
  selector: 'firmware-component-confirm-dialog',
  templateUrl: 'firmware.component.confirm.dialog.html',
})
export class FirmwareUpdateConfirmDialog {}

@Component({
  selector: 'firmware-component-result-dialog',
  templateUrl: 'firmware.component.result.dialog.html',
})
export class FirmwareUpdateResultDialog {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: FirmwareUpdateCommandOutput[]
  ) {}
}
