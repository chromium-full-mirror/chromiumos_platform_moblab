import {SelectionModel} from '@angular/cdk/collections';
import {Component, OnInit} from '@angular/core';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';
import {ConnectedDutFirmwareInfo} from 'app/services/moblabrpc_pb';

@Component({
  selector: 'app-firmware',
  templateUrl: './firmware.component.html',
  styleUrls: ['./firmware.component.scss']
})
export class FirmwareComponent implements OnInit {
  firmware_duts = [];
  firmwareDisplayedColumns: string[] =
      ['select', 'name', 'current_firmware', 'updater_firmware'];

  selection = new SelectionModel<ConnectedDutFirmwareInfo>(true, []);

  constructor(private moblabGrpcService: MoblabGrpcService) {}

  ngOnInit() {
    this.getConnectedDutsFirmware();
  }

  getConnectedDutsFirmware() {
    this.moblabGrpcService.listConnectedDutsFirmware(
        (connectedDutsFirmware: ConnectedDutFirmwareInfo[]) => {
          this.firmware_duts = connectedDutsFirmware;
          console.log(connectedDutsFirmware);
        });
  }

  updateFirmware() {
    const ips: string[] = [];
    this.firmware_duts.forEach(row => {
      if (this.selection.isSelected(row)) {
        ips.push(row.getIp());
      }
    });
    console.log(ips)
    
    this.moblabGrpcService.updateFirmwareOnDuts(ips, () => {
      this.getConnectedDutsFirmware();
    });
  }
}
