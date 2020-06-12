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

  chromeosReleaseVersion: string;
  chromeosReleaseTrack: string;
  chromeosReleaseDescription: string;
  moblabId: string;
  moblabSerialNumber: string;

  moblabHostname: string;
  isConnectedToInternet: boolean;

  loading = false;

  constructor(
    private changeDetector: ChangeDetectorRef,
    private snackBar: MatSnackBar,
    private moblabRpcService: MoblabGrpcService) {}

  ngOnInit(): void {
    this.getNetworkInfo();
    this.getCloudConfiguration();
    this.getVersionInfo();
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
    this.loading = true;
    this.moblabRpcService.get_cloud_configuration(
      (
        boto_key_id: string,
        boto_key_secret: string,
        gcs_bucket_url: string
      ) => {
        this.setCloudConfiguration(boto_key_id, boto_key_secret, gcs_bucket_url);
      },
      (errorMsg: string) => {
        this.loading = false;
        this.setOffPopup('Failed to get cloud configuration: ' + errorMsg);
      });
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

  setCloudConfiguration(boto_key_id, boto_key_secret, gcs_bucket_url) {
    console.log('setting');
    this.botoKeyIDForm.setValue(boto_key_id);
    this.botoKeySecretForm.setValue(boto_key_secret);
    this.bucketURLForm.setValue(gcs_bucket_url);

    this.bucketLink = 'https://console.cloud.google.com/storage/browser/' + gcs_bucket_url.split('//')[1];

    this.lastFetchedBotoKeyID = boto_key_id;
    this.lastFetchedBotoKeySecret = boto_key_secret;
    this.lastFetchedBucketURL = gcs_bucket_url;

    this.loading = false;
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

  disableSubmissionButton() {
    return !this.isCloudConfigurationChanged() ||
      this.botoKeySecretForm.errors ||
      this.botoKeyIDForm.errors ||
      this.bucketURLForm.errors;
  }

  ngAfterContentInit(): void {
    this.botoKeyIDForm.markAsTouched();
    this.botoKeySecretForm.markAsTouched();
    this.bucketURLForm.markAsTouched();
    this.changeDetector.detectChanges();
  }

  onSubmit(formValue) {
    this.loading = true;
    this.moblabRpcService.set_cloud_configuration(
      (
        message: string
      ) => {
        this.setOffPopup(message);
        this.getCloudConfiguration();
      },
      (errorMsg: string) => {
        this.loading = false;
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
}
