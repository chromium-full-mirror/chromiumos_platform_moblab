import {Component, OnInit} from '@angular/core';
import {MoblabGrpcService} from 'app/services/moblab-grpc.service';

@Component({
  selector: 'app-advanced-settings',
  templateUrl: './advanced-settings.component.html',
  styleUrls: ['./advanced-settings.component.scss'],
})
export class AdvancedSettingsComponent implements OnInit {
  constructor(private moblabRpcService: MoblabGrpcService) {}

  ngOnInit() {
    console.log('Hello');
    //   this.moblabRpcService.getConfigSettings().subscribe(
    //       response => {
    //         this.settings = response;
    //       },
    //       error => { console.log('Error happened' + error); },
    //       () => {});
  }
}
