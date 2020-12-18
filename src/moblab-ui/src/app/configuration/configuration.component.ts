import {
  AfterContentInit,
  ChangeDetectorRef,
  Component,
  OnInit,
  ViewChild
} from '@angular/core';

import {FormControl} from '@angular/forms';
import {Validators} from '@angular/forms';
import {MatSnackBar} from '@angular/material/snack-bar';

import {FileUploader} from 'ng2-file-upload';
import {MoblabGrpcService} from '../services/moblab-grpc.service';

const URL = 'https://google.com/api/';

function gsURLValidator(control) {
  if (!control.value) {
    return null;
  }
  const forbidden = !(new RegExp('^gs:\\/\\/.*\\/$').test(control.value));
  return forbidden ? {'notAGSUrl': {value: control.value}} : null;
}

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css']
})
export class ConfigurationComponent implements OnInit, AfterContentInit {
  errors = false;
  botoKeyIDForm = new FormControl('', {
    validators: [Validators.required],
  });

  botoKeySecretForm = new FormControl('', {
    validators: [Validators.required],
  });

  bucketURLForm = new FormControl('', {
    validators: [Validators.required, gsURLValidator],
  });
  bucketLink = '';
  lastFetchedBotoKeyID = '';
  lastFetchedBotoKeySecret = '';
  lastFetchedBucketURL = '';

  dutWifiInfoLoading = false;
  dutWifiNameForm = new FormControl('');
  dutWifiPasswordForm = new FormControl('');
  lastFetchedDutWifiName = '';
  lastFetchedDutWifiPassword = '';

  chromeosReleaseVersion: string;
  chromeosReleaseTrack: string;
  chromeosReleaseDescription: string;
  moblabId: string;
  moblabSerialNumber: string;

  moblabHostname: string;
  isConnectedToInternet: boolean;

  configurationLoading = false;

  constructor(
    private changeDetector: ChangeDetectorRef,
    private snackBar: MatSnackBar,
    private moblabRpcService: MoblabGrpcService) {}

  ngOnInit(): void {
    this.bucketURLForm.valueChanges.subscribe(value => {
      this.formatBucketLink();
    });

    this.getNetworkInfo();
    this.getCloudConfiguration();
    this.getVersionInfo();
    this.getDutWifiInfo();
  }

  getNetworkInfo() {
    this.moblabRpcService.get_network_info(
      (moblab_hostname: string, is_connected: boolean) => {
        this.setNetworkInfo(moblab_hostname, is_connected);
      },
      (errorMsg: string) => {
        console.log('Encountered failure getting network info. ', errorMsg);
      });
  }

  getCloudConfiguration() {
    this.configurationLoading = true;
    this.moblabRpcService.get_cloud_configuration(
      (
        boto_key_id: string,
        boto_key_secret: string,
        gcs_bucket_url: string
      ) => {
        this.setCloudConfiguration(boto_key_id, boto_key_secret, gcs_bucket_url);
      },
      (errorMsg: string) => {
        this.configurationLoading = false;
        this.setOffPopup('Failed to get cloud configuration: ' + errorMsg);
      });
  }

  getDutWifiInfo() {
    this.dutWifiInfoLoading = true;
    this.moblabRpcService.get_dut_wifi_info(
      (
        dut_wifi_name: string,
        dut_wifi_password: string,
      ) => {
        this.setDutWifiInfo(dut_wifi_name, dut_wifi_password);
      },
      (errorMsg: string) => {
        this.dutWifiInfoLoading = false;
        this.setOffPopup('Failed to get DUT wifi info: ' + errorMsg);
      });
  }

  onDutWifiInfoSubmit(formValue) {
    this.dutWifiInfoLoading = true;
    this.moblabRpcService.set_dut_wifi_info(
      (message: string) => {
        this.setOffPopup(message);
        this.getDutWifiInfo();
      },
      (errorMsg: string) => {
        this.dutWifiInfoLoading = false;
        this.setOffPopup(errorMsg);
      },
      this.dutWifiNameForm.value,
      this.dutWifiPasswordForm.value,);
  }

  getVersionInfo() {
    this.moblabRpcService.get_version_info(
      (
        chromeos_release_version: string,
        chromeos_release_track: string,
        chromeos_release_description: string,
        moblab_id: string,
        moblab_serial_number: string
      ) => {
        this.setVersionInfo(chromeos_release_version, chromeos_release_track, chromeos_release_description, moblab_id, moblab_serial_number);
      },
      (errorMsg: string) => {
        console.log('Encountered failure getting vesrion info. ', errorMsg);
      });
  }

  isCloudConfigurationChanged() {
    return this.lastFetchedBotoKeyID != this.botoKeyIDForm.value ||
      this.lastFetchedBotoKeySecret != this.botoKeySecretForm.value ||
      this.lastFetchedBucketURL != this.bucketURLForm.value
  }

  isDutWifiInfoChanged() {
    return this.lastFetchedDutWifiName != this.dutWifiNameForm.value ||
      this.lastFetchedDutWifiPassword != this.dutWifiPasswordForm.value;
  }

  setCloudConfiguration(boto_key_id, boto_key_secret, gcs_bucket_url) {
    console.log('setting');
    this.botoKeyIDForm.setValue(boto_key_id);
    this.botoKeySecretForm.setValue(boto_key_secret);
    this.bucketURLForm.setValue(gcs_bucket_url);

    this.lastFetchedBotoKeyID = boto_key_id;
    this.lastFetchedBotoKeySecret = boto_key_secret;
    this.lastFetchedBucketURL = gcs_bucket_url;

    this.configurationLoading = false;
  }

  private setDutWifiInfo(dut_wifi_name: string, dut_wifi_password: string) {
    this.dutWifiNameForm.setValue(dut_wifi_name);
    this.dutWifiPasswordForm.setValue(dut_wifi_password);

    this.lastFetchedDutWifiName = dut_wifi_name;
    this.lastFetchedDutWifiPassword = dut_wifi_password;

    this.dutWifiInfoLoading = false;
  }

  setNetworkInfo(moblab_hostname: string, is_connected: boolean) {
    this.moblabHostname = moblab_hostname;
    this.isConnectedToInternet = is_connected;
  }

  setVersionInfo(
    chromeos_release_version: string,
    chromeos_release_track: string,
    chromeos_release_description: string,
    moblab_id: string,
    moblab_serial_number: string
  ) {
    this.chromeosReleaseVersion = chromeos_release_version;
    this.chromeosReleaseTrack = chromeos_release_track;
    this.chromeosReleaseDescription = chromeos_release_description;
    this.moblabId = moblab_id;
    this.moblabSerialNumber = moblab_serial_number;
  }

  disableCloudConfigSubmissionButton() {
    return !this.isCloudConfigurationChanged() ||
      this.botoKeySecretForm.errors ||
      this.botoKeyIDForm.errors ||
      this.bucketURLForm.errors;
  }

  enableLink() {
    return !this.bucketURLForm.errors;
  }

  private formatBucketLink() {
    if (this.enableLink()) {
      this.bucketLink = 'https://console.cloud.google.com/storage/browser/' +
        this.bucketURLForm.value.split('//')[1];
    } else {
      this.bucketLink = '';
    }
  }

  ngAfterContentInit(): void {
    this.botoKeyIDForm.markAsTouched();
    this.botoKeySecretForm.markAsTouched();
    this.bucketURLForm.markAsTouched();
    this.changeDetector.detectChanges();
  }

  onCloudConfigSubmit(formValue) {
    this.configurationLoading = true;
    this.moblabRpcService.set_cloud_configuration(
      (message: string) => {
        this.setOffPopup(message);
        this.getCloudConfiguration();
      },
      (errorMsg: string) => {
        this.configurationLoading = false;
        this.setOffPopup(errorMsg);
      },
      this.botoKeyIDForm.value,
      this.botoKeySecretForm.value,
      this.bucketURLForm.value);
  }

  setOffPopup(dialogue: string) {
    const snackBarRef = this.snackBar.open(dialogue, '', {
      duration: 5000,
      verticalPosition: 'top'
    });
  }

  // ToDo: consolidate dialogs into sharable directory
  setOffError(dialogue: string) {
    const snackBarRef = this.snackBar.open(dialogue, 'Dismiss', {
      verticalPosition: 'top',
      panelClass: ["snack-error"],
    });
  }

  updateCloudConfigurationForms(
    boto_key_id: string,
    boto_key_secret: string,
    gcs_bucket_url: string,
    is_cloud_enabled: boolean,
    is_remote_console_enabled: boolean,
    is_remote_command_enabled: boolean
  ) {
    /**
     * Updates the form values of the cloud configurations. Meant to be called
     * with values returned from RPC call to get cloud info.
     */
    this.botoKeyIDForm.setValue(boto_key_id);
    this.botoKeySecretForm.setValue(boto_key_secret);
    this.bucketURLForm.setValue(gcs_bucket_url);

    this.lastFetchedBotoKeyID = boto_key_id;
    this.lastFetchedBotoKeySecret = boto_key_secret;
    this.lastFetchedBucketURL = gcs_bucket_url;

    this.isCloudEnabled = is_cloud_enabled;
    this.isRemoteConsoleEnabled = is_remote_console_enabled;
    this.isRemoteCommandEnabled = is_remote_command_enabled;

    this.toggleCloudConfigDisabledMessage();

    this.lastFetchedIsCloudEnabled = this.isCloudEnabled;
    this.lastFetchedIsRemoteConsoleEnabled = this.isRemoteConsoleEnabled;
    this.lastFetchedIsRemoteCommandEnabled = this.isRemoteCommandEnabled;

    this.configurationLoading = false;
  }

  public async pauseClick() {
    this.pauseButton.setIsLoadingStatus(true);
    try {
      const pauseRequesters = await this.moblabConfigurationRpcService.pause_host_scheduling();
      this.settingsService.updateHostSchedulingStatus(pauseRequesters);
    }
    catch (error) {
      console.log('pause_host_scheduling call failed with:' + error);
      this.setOffError('Failed to pause host scheduling: ' + error);
    }
    finally {
      this.pauseButton.setIsLoadingStatus(false);
    }
  }

  public async resumeClick() {
    this.resumeButton.setIsLoadingStatus(true);
    try {
      const pauseRequesters = await this.moblabConfigurationRpcService.resume_host_scheduler()
      this.settingsService.updateHostSchedulingStatus(pauseRequesters);
    }
    catch (error) {
      console.log('resume_host_scheduler call failed with:' + error);
      this.setOffError('Failed to resume host scheduling: ' + error);
    }
    finally {
      this.resumeButton.setIsLoadingStatus(false);
    }
  }
}
