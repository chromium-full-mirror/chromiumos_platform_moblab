import {
  Component,
  EventEmitter,
  ViewChild
} from '@angular/core';

import {LoadingOverlayComponent} from '../widgets/loading-overlay/loading-overlay.component';

@Component({
  selector: 'app-run-suite',
  templateUrl: './run-suite.component.html',
  styleUrls: ['./run-suite.component.css'],
})
export class RunSuiteComponent {
  @ViewChild(LoadingOverlayComponent) loadingOverlay: LoadingOverlayComponent;

  onSuiteStart() {
    this.onSuiteStatusUpdate('submitting');
    this.loadingOverlay.show();
  }

  onSuiteStatusUpdate(current_state: string) {
    this.loadingOverlay.updateStatus(current_state);
  }
}
