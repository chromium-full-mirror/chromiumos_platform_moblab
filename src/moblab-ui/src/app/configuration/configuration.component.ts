import {
  AfterContentInit,
  ChangeDetectorRef,
  Component,
  OnInit,
  ViewChild,
} from '@angular/core';
import {FormControl, Validators} from '@angular/forms';
import {MatSnackBar} from '@angular/material/snack-bar';

import {leadingTrailingWhitespaceValidator} from '../utils/validators';
import {MoblabGrpcService} from '../services/moblab-grpc.service';
import {MoblabConfigurationGrpcService} from '../services/moblab-configuration-grpc.service';
import {MoblabSettingsService} from '../services/moblab-settings.service';
import {ButtonWithProgressComponent} from '../widgets/button-with-progress/button-with-progress.component';
import {MoblabSettingsConstains} from '../constants';

function gsURLValidator(control) {
  if (!control.value) {
    return null;
  }
  const forbidden = !new RegExp('^gs:\\/\\/.*\\/$').test(control.value);
  return forbidden ? {notAGSUrl: {value: control.value}} : null;
}

class CloudConfiguration {
  constructor(
    public isCloudEnabled: boolean = false,
    public isRemoteConsoleEnabled: boolean = false,
    public isRemoteCommandEnabled: boolean = false,
    public botoKeyID: string = '',
    public botoKeySecret: string = '',
    public bucketURL: string = ''
  ) {}
}

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.scss'],
})
export class ConfigurationComponent implements OnInit, AfterContentInit {
  @ViewChild('pauseButton') pauseButton: ButtonWithProgressComponent;
  @ViewChild('resumeButton') resumeButton: ButtonWithProgressComponent;
  errors = false;

  canUpdateCloudConfig = false;

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

  userCrOSVersionForm = new FormControl(
    '',
    Validators.pattern(/^R[0-9]{2,3}-[0-9]{5,}\.[0-9]{1,}\.[0-9]{1,}$/)
  );
  defaultCrOSVersionForm = new FormControl('');

  userCrOSVersionValue = 'None';

  bucketLink = '';
  cloudConfigDisabledMessage = '';

  showUncheckWarning = false;
  configurationLoading = false;

  lastFetchedCloudConfig = new CloudConfiguration();

  dutWifiInfoLoading = false;
  dutWifiNameForm = new FormControl('', {
    validators: [leadingTrailingWhitespaceValidator],
  });
  dutWifiPasswordForm = new FormControl('');
  lastFetchedDutWifiName = '';
  lastFetchedDutWifiPassword = '';

  moblabReleaseVersion = '';
  chromeosReleaseVersion = '';
  chromeosReleaseTrack = '';
  chromeosReleaseDescription = '';
  moblabInstallId = '';
  moblabSerialNumber = '';

  moblabHostname = '';
  isConnectedToInternet = false;

  constructor(
    private changeDetector: ChangeDetectorRef,
    private moblabRpcService: MoblabGrpcService,
    private snackBar: MatSnackBar,
    private settingsService: MoblabSettingsService,
    private moblabConfigurationRpcService: MoblabConfigurationGrpcService
  ) {}

  async ngOnInit(): Promise<void> {
    this.bucketURLForm.valueChanges.subscribe(value => {
      this.formatBucketLink();
    });
    this.settingsService.pauseRequestorsObservable.subscribe(requestors => {
      this.isHostSchedulerPauseRequested =
        requestors &&
        requestors.includes(MoblabSettingsConstains.USER_REQUEST_STRING);
    });
    this.getNetworkInfo();
    this.getCloudConfiguration();
    this.getVersionInfo();
    this.getDutWifiInfo();
    this.defaultCrOSVersionForm.disable();
    this.initCanUpdateCloudConfigFlag();
    await this.getStableCrOSVersion();
  }

  public async getStableCrOSVersion() {
    this.userCrOSVersionForm.disable();
    try {
      const version = await this.moblabConfigurationRpcService.getStableBuildVersion();
      this.userCrOSVersionValue = version.UserOverrideVersion;
      this.userCrOSVersionForm.setValue(version.UserOverrideVersion);
      this.defaultCrOSVersionForm.setValue(version.DefaultVersion);
    } catch (error) {
      console.log('getStableBuildVersion call failed with:' + error);
      this.setOffError('Failed to fetch stable Chrome OS version: ' + error);
    } finally {
      this.userCrOSVersionForm.enable();
    }
  }

  public async setStableCrOSVersion(override_value: string) {
    this.userCrOSVersionForm.disable();
    try {
      const version = await this.moblabConfigurationRpcService.setStableBuildVersion(
        override_value
      );
      this.userCrOSVersionValue = version.UserOverrideVersion;
      this.userCrOSVersionForm.setValue(version.UserOverrideVersion);
      this.defaultCrOSVersionForm.setValue(version.DefaultVersion);
    } catch (error) {
      console.log('setStableBuildVersion call failed with:' + error);
      this.setOffError('Failed to fetch stable Chrome OS version: ' + error);
    } finally {
      this.userCrOSVersionForm.enable();
    }
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
          new CloudConfiguration(
            is_cloud_enabled,
            is_remote_console_enabled,
            is_remote_command_enabled,
            boto_key_id,
            boto_key_secret,
            gcs_bucket_url
          )
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
          'R2-7.0',//moblab_release_version,
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
      this.lastFetchedCloudConfig.botoKeyID !== this.botoKeyIDForm.value ||
      this.lastFetchedCloudConfig.botoKeySecret !==
        this.botoKeySecretForm.value ||
      this.lastFetchedCloudConfig.bucketURL !== this.bucketURLForm.value ||
      this.lastFetchedCloudConfig.isCloudEnabled !== this.isCloudEnabled ||
      this.lastFetchedCloudConfig.isRemoteConsoleEnabled !==
        this.isRemoteConsoleEnabled ||
      this.lastFetchedCloudConfig.isRemoteCommandEnabled !==
        this.isRemoteCommandEnabled
    );
  }

  isDutWifiInfoValidForSubmit() {
    return (
      this.dutWifiNameForm.value.length &&
      !this.dutWifiNameForm.errors &&
      !this.dutWifiPasswordForm.errors &&
      (this.lastFetchedDutWifiName !== this.dutWifiNameForm.value ||
        this.lastFetchedDutWifiPassword !== this.dutWifiPasswordForm.value)
    );
  }

  isStableCrOsVersionValidForSubmit() {
    return (
      this.userCrOSVersionForm.value !== this.userCrOSVersionValue &&
      !this.userCrOSVersionForm.errors
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

    if (this.isCloudEnabled) {
      this.isRemoteCommandEnabled = true;
      this.isRemoteConsoleEnabled = true;
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
    this.changeDetector.detectChanges();
  }

  /** Checks if the Moblab has ran some jobs already,
   * if so user can not change the boto key or gc bucket. */
  initCanUpdateCloudConfigFlag() {
    this.botoKeyIDForm.disable();
    this.botoKeySecretForm.disable();
    this.bucketURLForm.disable();
    this.canUpdateCloudConfig = false;
    this.moblabRpcService.getNumJobs((count: number) => {
      this.canUpdateCloudConfig = count === 0;

      if (this.canUpdateCloudConfig) {
        this.botoKeyIDForm.enable();
        this.botoKeySecretForm.enable();
        this.bucketURLForm.enable();
      }
    });
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
      this.isCloudEnabled ? this.botoKeyIDForm.value : '',
      this.isCloudEnabled ? this.botoKeySecretForm.value : '',
      this.isCloudEnabled ? this.bucketURLForm.value : '',
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

  updateCloudConfigurationForms(newCloudConfig: CloudConfiguration) {
    /**
     * Updates the form values of the cloud configurations. Meant to be called
     * with values returned from RPC call to get cloud info.
     */
    this.botoKeyIDForm.setValue(newCloudConfig.botoKeyID);
    this.botoKeySecretForm.setValue(newCloudConfig.botoKeySecret);
    this.bucketURLForm.setValue(newCloudConfig.bucketURL);

    this.isCloudEnabled = newCloudConfig.isCloudEnabled;
    this.isRemoteConsoleEnabled = newCloudConfig.isRemoteConsoleEnabled;
    this.isRemoteCommandEnabled = newCloudConfig.isRemoteCommandEnabled;

    this.toggleCloudConfigDisabledMessage();

    this.lastFetchedCloudConfig = newCloudConfig;

    this.configurationLoading = false;
  }

  public async pauseClick() {
    this.pauseButton.setIsLoadingStatus(true);
    try {
      const pauseRequesters = await this.moblabConfigurationRpcService.pauseHostScheduling();
      this.settingsService.updateHostSchedulingStatus(pauseRequesters);
    } catch (error) {
      console.log('pauseHostScheduling call failed with:' + error);
      this.setOffError('Failed to pause host scheduling: ' + error);
    } finally {
      this.pauseButton.setIsLoadingStatus(false);
    }
  }

  public async resumeClick() {
    this.resumeButton.setIsLoadingStatus(true);
    try {
      const pauseRequesters = await this.moblabConfigurationRpcService.resumeHostScheduler();
      this.settingsService.updateHostSchedulingStatus(pauseRequesters);
    } catch (error) {
      console.log('resumeHostScheduler call failed with:' + error);
      this.setOffError('Failed to resume host scheduling: ' + error);
    } finally {
      this.resumeButton.setIsLoadingStatus(false);
    }
  }
}
