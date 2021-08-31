import {Component, OnInit} from '@angular/core';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';

@Component({
  selector: 'app-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.scss'],
})
export class AboutComponent implements OnInit {
  moblabReleaseVersion = '';
  chromeosReleaseVersion = '';
  chromeosReleaseTrack = '';
  chromeosReleaseDescription = '';
  moblabInstallId = '';
  moblabSerialNumber = '';

  moblabHostname = '';
  moblabMacAddress = '';
  isConnectedToInternet = false;

  constructor(private moblabRpcService: MoblabGrpcService) { }

  ngOnInit(): void {
    this.getVersionInfo();
    this.getNetworkInfo();
  }

  refreshShownVersionInfo(
    moblab_release_version: string,
    chromeos_release_version: string,
    chromeos_release_track: string,
    chromeos_release_description: string,
    moblab_install_id: string,
    moblab_serial_number: string
  ) {
    // local setter of variables that are shown in the config UI ( not to be confused with getter/setters that commit and
    // fetch changes from actual backend. )
    this.moblabReleaseVersion = moblab_release_version;
    this.chromeosReleaseVersion = chromeos_release_version;
    this.chromeosReleaseTrack = chromeos_release_track;
    this.chromeosReleaseDescription = chromeos_release_description;
    this.moblabInstallId = moblab_install_id;
    this.moblabSerialNumber = moblab_serial_number;
  }

  getVersionInfo() {
    this.moblabRpcService.get_version_info(
      (
        moblab_release_version: string,
        chromeos_release_version: string,
        chromeos_release_track: string,
        chromeos_release_description: string,
        moblab_install_id: string,
        moblab_serial_number: string
      ) => {
        this.refreshShownVersionInfo(
          moblab_release_version,
          chromeos_release_version,
          chromeos_release_track,
          chromeos_release_description,
          moblab_install_id,
          moblab_serial_number
        );
      },
      (errorMsg: string) => {
        console.log('Encountered failure getting version info. ', errorMsg);
      }
    );
  }

  getNetworkInfo() {
    this.moblabRpcService.get_network_info(
      (
        moblab_hostname: string,
        moblab_mac_address: string,
        is_connected: boolean
      ) => {
        this.moblabHostname = moblab_hostname;
        this.moblabMacAddress = moblab_mac_address;
        this.isConnectedToInternet = is_connected;
      },
      (errorMsg: string) => {
        console.log('Encountered failure getting network info. ', errorMsg);
      }
    );
  }
}
