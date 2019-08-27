import {Component, Pipe} from '@angular/core';
import {MoblabGrpcService} from '../services/moblab-grpc.service';


@Component({
  selector: 'app-advanced-settings',
  template: `
  <content md-content>
    <div *ngFor="let sectionKeyValuePair of settings | mapToIterable">
      <mat-card >
        {{sectionKeyValuePair.key}}
        <div *ngFor="let settingKeyPairValue of sectionKeyValuePair.value">
        {{settingKeyPairValue.value}}
        </div>
      </mat-card>
     <p></p></div>
  </content>
    `,
})

export class AdvancedSettingsComponent {

  settings: Map<string, string[][]> = new Map();

  constructor(private moblabRpcService: MoblabGrpcService) { }

  AfterViewInit() {
    console.log('Hello');
  //   this.moblabRpcService.getConfigSettings().subscribe(
  //       response => {
  //         this.settings = response;
  //       },
  //       error => { console.log('Error happened' + error); },
  //       () => {});
  }
}


