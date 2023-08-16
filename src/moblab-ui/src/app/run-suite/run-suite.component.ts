import {Component, ViewChild} from '@angular/core';

import {SuiteChangeType} from './common/base_suite/base-suite.component';
import {
  LoadingOverlayComponent,
  LoadingOverlayStyle,
} from '../widgets/loading-overlay/loading-overlay.component';
import {GlobalInfoService} from 'app/services/services.module';
import {Feature} from 'app/services/services.module';

@Component({
  selector: 'app-run-suite',
  templateUrl: './run-suite.component.html',
  styleUrls: ['./run-suite.component.scss'],
})
export class RunSuiteComponent {
  @ViewChild(LoadingOverlayComponent) loadingOverlay: LoadingOverlayComponent;

  constructor(private globalInfo: GlobalInfoService) {}

  onSuiteStart() {
    this.onSuiteStatusUpdate('submitting');
    this.loadingOverlay.show();
  }

  onSuiteFormChange(changeType: SuiteChangeType, message: string = null) {
    if (!this.loadingOverlay) {
      return;
    }

    if (changeType === SuiteChangeType.RunSuiteStart) {
      this.onSuiteStatusUpdate('submitting');
      this.loadingOverlay.show();
    } else if (changeType === SuiteChangeType.RunSuiteFailed) {
      this.loadingOverlay.hide();
    } else if (changeType === SuiteChangeType.FormLoadingStart) {
      this.loadingOverlay.updateStatus(message, LoadingOverlayStyle.Top);
    } else if (changeType === SuiteChangeType.FormLoadingFinish) {
      this.loadingOverlay.hide();
    }
  }

  onLoadingStart(message) {
    this.loadingOverlay.updateStatus(message, LoadingOverlayStyle.Top);
  }

  onLoadingFinish() {
    this.loadingOverlay.hide();
  }

  onSuiteStatusUpdate(current_state: string) {
    this.loadingOverlay.updateStatus(current_state);
  }

  isTestEnabled(feature: Feature) {
    return this.globalInfo.isFeatureEnabled(feature);
  }
}
