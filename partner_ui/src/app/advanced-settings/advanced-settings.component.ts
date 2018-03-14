import {Component, Pipe} from '@angular/core';
import {MoblabRpcService} from '../services/moblab-rpc.service';
import {MapToIterable} from '../utils/map-to-iterable';


@Component({
  selector: 'advanced-settings',
  template: `
  <content md-content>
    <div *ngFor="let sectionKeyValuePair of settings | mapToIterable">
      <md-card >
        {{sectionKeyValuePair.key}}
        <div *ngFor="let settingKeyPairValue of sectionKeyValuePair.value">
        {{settingKeyPairValue.value}}
        </div>
      </md-card>
     <p></p></div>
  </content>
        
        
    `,
})

export class AdvancedSettingsComponent {

  constructor(private moblabRpcService: MoblabRpcService) { }

  settings: Map<string, Array<Array<string>>> = new Map();

  ngAfterViewInit(){
    this.moblabRpcService.getConfigSettings().subscribe(
        response => {
          this.settings = response;
        },
        error => { console.log("Error happened" + error) },
        () => {});
  }
}


