import {
  AfterContentInit,
  ChangeDetectorRef,
  Component,
  OnInit,
  ViewChild,
} from '@angular/core';
import {FormControl} from '@angular/forms';
import {MatSnackBar} from '@angular/material/snack-bar';
import {Validators} from '@angular/forms';

import {leadingTrailingWhitespaceValidator} from '../utils/validators';
import {MoblabGrpcService} from '../services/moblab-grpc.service';
import {MoblabConfigurationGrpcService} from '../services/moblab-configuration-grpc.service';
import {MoblabSettingsService} from '../services/moblab-settings.service';
import {ButtonWithProgressComponent} from '../widgets/button-with-progress/button-with-progress.component';
import {MoblabSettingsConstains} from '../constants';

const URL = 'https://google.com/api/';

function gsURLValidator(control) {
  if (!control.value) {
    return null;
  }
  const forbidden = !new RegExp('^gs:\\/\\/.*\\/$').test(control.value);
  return forbidden ? {notAGSUrl: {value: control.value}} : null;
}

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css'],
})
export class ConfigurationComponent implements OnInit, AfterContentInit {
  @ViewChild('pauseButton') pauseButton: ButtonWithProgressComponent;
  @ViewChild('resumeButton') resumeButton: ButtonWithProgressComponent;
  errors = false;
  isCloudEnabled = false;
  isRemoteConsoleEnabled = false;
  isRemoteCommandEnabled = false;
  isHostSchedulerPauseRequested = false;

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
  cloudConfigDisabledMessage = '';

  showUncheckWarning = false;
  configurationLoading = false;

  lastFetchedIsCloudEnabled = false;
  lastFetchedIsRemoteConsoleEnabled = false;
  lastFetchedIsRemoteCommandEnabled = false;
  lastFetchedBotoKeyID = '';
  lastFetchedBotoKeySecret = '';
  lastFetchedBucketURL = '';

  dutWifiInfoLoading = false;
  dutWifiNameForm = new FormControl('', {
    validators: [leadingTrailingWhitespaceValidator],
  });
  dutWifiPasswordForm = new FormControl('');
  lastFetchedDutWifiName = '';
  lastFetchedDutWifiPassword = '';

  chromeosReleaseVersion: string;
  chromeosReleaseTrack: string;
  chromeosReleaseDescription: string;
  moblabInstallId: string;
  moblabSerialNumber: string;

  moblabHostname: string;
  isConnectedToInternet: boolean;

  constructor(
    private changeDetector: ChangeDetectorRef,
    private moblabRpcService: MoblabGrpcService,
    private snackBar: MatSnackBar,
    private settingsService: MoblabSettingsService,
    private moblabConfigurationRpcService: MoblabConfigurationGrpcService
  ) {}

  ngOnInit(): void {
    this.bucketURLForm.valueChanges.subscribe(value => {
      this.formatBucketLink();
    });
    this.settingsService.pauseRequestors.subscribe(requestors => {
      this.isHostSchedulerPauseRequested =
        requestors &&
        requestors.includes(MoblabSettingsConstains.USER_REQUEST_STRING);
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
      }
    );
  }

  getCloudConfiguration() {
    /**
     * Method sends RPC command to fetch cloud configuration information and
     * apply fetched values to the UI forms.
     */
    this.configurationLoading = true;
    this.moblabRpcService.get_cloud_configuration(
      (
        boto_key_id: string,
        boto_key_secret: string,
        gcs_bucket_url: string,
        is_cloud_enabled: boolean,
        is_remote_console_enabled: boolean,
        is_remote_command_enabled: boolean
      ) => {
        this.updateCloudConfigurationForms(
          boto_key_id,
          boto_key_secret,
          gcs_bucket_url,
          is_cloud_enabled,
          is_remote_console_enabled,
          is_remote_command_enabled
        );
      },
      (errorMsg: string) => {
        this.configurationLoading = false;
        this.setOffPopup('Failed to get cloud configuration: ' + errorMsg);
      }
    );
  }

  getDutWifiInfo() {
    this.dutWifiInfoLoading = true;
    this.moblabRpcService.get_dut_wifi_info(
      (dut_wifi_name: string, dut_wifi_password: string) => {
        this.setDutWifiInfo(dut_wifi_name, dut_wifi_password);
      },
      (errorMsg: string) => {
        this.dutWifiInfoLoading = false;
        this.setOffPopup('Failed to get DUT wifi info: ' + errorMsg);
      }
    );
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
      this.dutWifiPasswordForm.value
    );
  }

  getVersionInfo() {
    this.moblabRpcService.get_version_info(
      (
        chromeos_release_version: string,
        chromeos_release_track: string,
        chromeos_release_description: string,
        moblab_install_id: string,
        moblab_serial_number: string
      ) => {
        this.refreshShownVersionInfo(
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

  isCloudConfigurationChanged() {
    /**
     * Returns true IFF there is a change in any of the cloud configuration
     * values.
     */
    return (
      this.lastFetchedBotoKeyID != this.botoKeyIDForm.value ||
      this.lastFetchedBotoKeySecret != this.botoKeySecretForm.value ||
      this.lastFetchedBucketURL != this.bucketURLForm.value ||
      this.lastFetchedIsCloudEnabled != this.isCloudEnabled ||
      this.lastFetchedIsRemoteConsoleEnabled != this.isRemoteConsoleEnabled ||
      this.lastFetchedIsRemoteCommandEnabled != this.isRemoteCommandEnabled
    );
  }

  isDutWifiInfoValidForSubmit() {
    return (
      this.dutWifiNameForm.value.length &&
      !this.dutWifiNameForm.errors &&
      !this.dutWifiPasswordForm.errors &&
      (this.lastFetchedDutWifiName != this.dutWifiNameForm.value ||
        this.lastFetchedDutWifiPassword != this.dutWifiPasswordForm.value)
    );
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

  refreshShownVersionInfo(
    chromeos_release_version: string,
    chromeos_release_track: string,
    chromeos_release_description: string,
    moblab_install_id: string,
    moblab_serial_number: string
  ) {
    // local setter of variables that are shown in the config UI ( not to be confused with getter/setters that commit and
    // fetch changes from actual backend. )
    this.chromeosReleaseVersion = chromeos_release_version;
    this.chromeosReleaseTrack = chromeos_release_track;
    this.chromeosReleaseDescription = chromeos_release_description;
    this.moblabInstallId = moblab_install_id;
    this.moblabSerialNumber = moblab_serial_number;
  }

  disableCloudConfigSubmissionButton() {
    return (
      !this.isCloudConfigurationChanged() ||
      this.botoKeySecretForm.errors ||
      this.botoKeyIDForm.errors ||
      this.bucketURLForm.errors
    );
  }

  enableLink() {
    return !this.bucketURLForm.errors;
  }

  private formatBucketLink() {
    if (this.enableLink()) {
      this.bucketLink =
        'https://console.cloud.google.com/storage/browser/' +
        this.bucketURLForm.value.split('//')[1];
    } else {
      this.bucketLink = '';
    }
  }

  toggleCloudConfigDisabledMessage() {
    /**
     * Will set tooltip hover of cloud configuration forms to show that cloud
     * integration needs to be enabled before any change is made.
     */
    if (this.isCloudEnabled) {
      this.cloudConfigDisabledMessage = '';
    } else {
      this.cloudConfigDisabledMessage =
        "Cloud settings are not enabled, please check 'enable' above if you would " +
        ' like to opt-in to cloud interaction for your Moblab.';
    }
  }

  isCloudEnabledCheckboxChange() {
    /**
     * Invoked on change of cloud enabled checkbox.
     */
    this.isCloudEnabled = !this.isCloudEnabled;

    if (!this.isCloudEnabled) {
      this.isRemoteConsoleEnabled = false;
      this.isRemoteCommandEnabled = false;
      // clears boto and GCS bucket configurations, leaves cloud and remote console / remote commands enable settings unchanged.
      this.updateCloudConfigurationForms(
        '', // boto_key_id
        '', // boto_key_secret
        '', // gcs_bucket_url
        this.isCloudEnabled,
        this.isRemoteConsoleEnabled,
        this.isRemoteCommandEnabled
      );
    }
    this.toggleCloudConfigDisabledMessage();
  }

  isRemoteConsoleEnabledCheckboxChange() {
    /**
     * Invoked on change of remote console enabled checkbox.
     */
    this.isRemoteConsoleEnabled = !this.isRemoteConsoleEnabled;
  }

  isRemoteCommandEnabledCheckboxChange() {
    /**
     * Invoked on change of remote command enabled checkbox.
     */
    this.isRemoteCommandEnabled = !this.isRemoteCommandEnabled;
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
      this.bucketURLForm.value,
      this.isCloudEnabled,
      this.isRemoteConsoleEnabled,
      this.isRemoteCommandEnabled
    );
  }

  cloudCheckboxHoverStart() {
    /**
     * Invoked on mouseover of the enable cloud checkbox. Will associate error
     * messages on cloud configuration forms that unchecking cloud integration
     * will clear existing cloud config values ( error messages are set only if
     * the cloud checkbox in enabled during mouseover and there is at least one
     * non-empty cloud configuration ).
     */
    if (
      this.isCloudEnabled &&
      (this.botoKeyIDForm.value ||
        this.botoKeySecretForm.value ||
        this.bucketURLForm.value)
    ) {
      this.showUncheckWarning = true;
      const clearError = {clearWarning: true};

      this.botoKeyIDForm.setErrors(clearError);
      this.botoKeySecretForm.setErrors(clearError);
      this.bucketURLForm.setErrors(clearError);
    }
  }

  cloudCheckboxHoverStop() {
    /**
     * Invoked on mouseoff of the enable cloud checkbox. Will clear the error
     * set by cloudCheckboxHoverStart
     */
    if (
      this.botoKeyIDForm.value ||
      this.botoKeySecretForm.value ||
      this.bucketURLForm.value
    ) {
      this.botoKeyIDForm.setErrors(null);
      this.botoKeySecretForm.setErrors(null);
      this.bucketURLForm.setErrors(null);

      this.botoKeyIDForm.updateValueAndValidity();
      this.botoKeySecretForm.updateValueAndValidity();
      this.bucketURLForm.updateValueAndValidity();
    }
  }

  setOffPopup(dialogue: string) {
    const snackBarRef = this.snackBar.open(dialogue, '', {
      duration: 5000,
      verticalPosition: 'top',
    });
  }

  // ToDo: consolidate dialogs into sharable directory
  setOffError(dialogue: string) {
    const snackBarRef = this.snackBar.open(dialogue, 'Dismiss', {
      verticalPosition: 'top',
      panelClass: ['snack-error'],
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
    } catch (error) {
      console.log('pause_host_scheduling call failed with:' + error);
      this.setOffError('Failed to pause host scheduling: ' + error);
    } finally {
      this.pauseButton.setIsLoadingStatus(false);
    }
  }

  public async resumeClick() {
    this.resumeButton.setIsLoadingStatus(true);
    try {
      const pauseRequesters = await this.moblabConfigurationRpcService.resume_host_scheduler();
      this.settingsService.updateHostSchedulingStatus(pauseRequesters);
    } catch (error) {
      console.log('resume_host_scheduler call failed with:' + error);
      this.setOffError('Failed to resume host scheduling: ' + error);
    } finally {
      this.resumeButton.setIsLoadingStatus(false);
    }
  }
}
