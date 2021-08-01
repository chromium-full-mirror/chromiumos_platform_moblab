import {Component, OnInit} from '@angular/core';
import {GlobalInfoService} from 'app/services/services.module';
import {Feature} from 'app/services/services.module';


@Component({
  selector: 'app-advanced-settings',
  templateUrl: './advanced-settings.component.html',
  styleUrls: ['./advanced-settings.component.scss'],
})
export class AdvancedSettingsComponent implements OnInit {
  constructor(private globalInfo: GlobalInfoService) { }

  faftEnabled = false;

  ngOnInit() {
    this.faftEnabled = this.globalInfo.isFeatureEnabled(Feature.FAFT_TESTING);
  }

  saveFAFTSetting(newValue) {
    if (newValue === true) {
      this.globalInfo.enableFeature(Feature.FAFT_TESTING);
    } else {
      this.globalInfo.disableFeature(Feature.FAFT_TESTING);
    }
  }
}
