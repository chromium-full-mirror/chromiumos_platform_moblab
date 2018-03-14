import { Component, ViewChild } from '@angular/core';
import { MoblabRpcService } from '../services/moblab-rpc.service';
import { FileUploader } from 'ng2-file-upload';
import { Observable } from 'rxjs';

const URL = 'https://google.com/api/';

@Component({
  selector: 'configuration',
  templateUrl: './configuration.component.html',
  styles: [`
    .configuration-label {
      min-width: 250px;
      margin: 10px;
    }
    .configuration-input {
      margin-right: 15px;
      min-width: 400px;
    }
    .configuration {
      flex-direction: row;
      layout-margin: 50px;
    }
    
    md-input-container .ng-invalid {
      border:3px solid red;
    }
    
    md-card-header {
      text-decoration: underline;
      font-size: 18px;
    }

    `],
})

export class ConfigurationComponent {

  constructor(private moblabRpcService: MoblabRpcService) { }

  botoKeyId: string;
  botoKeySecret: string;
  imageStorageUrl: string;
  imageStorageLink: string = "https://console.cloud.google.com/storage/browser/chromeos-moblab-haddowktest/"
  cloudNotificationTopic: string = "moblab-notification"
  moblabVersion: string;
  moblabTrack: string;
  moblabDescription: string;
  moblabId: string;
  moblabMacAddress: string;
  cloudNotificationEnabled: boolean = false;
  serverIp: string;
  isConnectedToInternet: string;
  disableSaveButton: boolean = false;


  uploader:FileUploader = new FileUploader({url: URL});

  @ViewChild('formRef') form;

  ngOnInit() : void {

  }

  onSubmit(formValue){
    console.log(formValue);
  }

  ngAfterViewInit(){
    this.moblabRpcService.getCloudStorageInformation().subscribe(
        response => {
          this.botoKeyId = response['gs_access_key_id'];
          this.botoKeySecret = response['gs_secret_access_key'];
          this.imageStorageUrl = response['image_storage_server'];
        },
        error => { console.log("Error happened" + error) },
        () => {});

    this.moblabRpcService.getNetworkInformation().subscribe(
        response => {
          this.serverIp = response['server_ips'][0];
          this.isConnectedToInternet = response['is_connected'];
        },
        error => { console.log("Error happened" + error) },
        () => {});

    this.moblabRpcService.getVersionInformation().subscribe(
        response => {
          this.moblabVersion = "R" + response['CHROMEOS_RELEASE_CHROME_MILESTONE'] + "." + response['CHROMEOS_RELEASE_VERSION'];
          this.moblabTrack = response['CHROMEOS_RELEASE_TRACK'];
          this.moblabDescription = response['CHROMEOS_RELEASE_DESCRIPTION'];
          this.moblabId = response['MOBLAB_ID'];
          this.moblabMacAddress = response['MOBLAB_MAC_ADDRESS'];
        },
        error => { console.log("Error happened" + error) },
        () => {});
    this.moblabRpcService.getConfigSettings().subscribe(
        response => {
          console.log(response);
          console.log(response["CROS"]);
          for (var setting of response["CROS"]){
            if (setting[0] == "cloud_notification_topic") {
              this.cloudNotificationTopic = setting[1]
            }
          }
        },
        error => { console.log("Error happened" + error) },
        () => {});
    // Observable.combineLatest(
    //     this.form.statusChanges,
    //     this.form.valueChanges,
    //     (status, value)=> ({status, value})
    //     )
    //     .filter(({status})=> status === 'VALID')
    //     .subscribe(({value})=> console.log(value))
  }

}


