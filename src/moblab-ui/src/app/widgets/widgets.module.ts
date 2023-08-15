import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {BrowserModule} from '@angular/platform-browser';
import {CommonModule} from '@angular/common';
import {ConfirmationDialog} from './confirmation-dialog/confirmation-dialog.component';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatDialogModule} from '@angular/material/dialog';
import {MatIconModule} from '@angular/material/icon';
import {MatListModule} from '@angular/material/list';
import {MatProgressBarModule} from '@angular/material/progress-bar';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatSelectModule} from '@angular/material/select';
import {MatTableModule} from '@angular/material/table';
import {MatTooltipModule} from '@angular/material/tooltip';
import {NgModule} from '@angular/core';

import {KeyValTableComponent} from './keyval-table/keyval-table.component';
import {LoadingOverlayComponent} from './loading-overlay/loading-overlay.component';
import {RebootButtonComponent} from './reboot-button/reboot-button.component';
import {TableHeaderSelectorComponent} from './table-header-selector/table-header-selector.component';
import {UpdateButtonComponent} from './update-button/update-button.component';

import {
  FeedbackComponent,
  SubmissionResultDialog,
} from './feedback/feedback.component';
import {FeedbackModule as ScreenshotFeedbackModule} from '../third_party/feedback/feedback.module';
import {NewUpdateModule} from '../directives/new-update/new-update.module';
import {ButtonWithProgressComponent} from './button-with-progress/button-with-progress.component';
import {NotificationBannerComponent} from './notification-banner/notification-banner.component';
import {NewUpdateComponent} from './new-update/new-update.component';

@NgModule({
  declarations: [
    ConfirmationDialog,
    FeedbackComponent,
    KeyValTableComponent,
    LoadingOverlayComponent,
    RebootButtonComponent,
    SubmissionResultDialog,
    TableHeaderSelectorComponent,
    UpdateButtonComponent,
    ButtonWithProgressComponent,
    NotificationBannerComponent,
    NewUpdateComponent,
  ],
  exports: [
    FeedbackComponent,
    KeyValTableComponent,
    LoadingOverlayComponent,
    RebootButtonComponent,
    TableHeaderSelectorComponent,
    UpdateButtonComponent,
    ButtonWithProgressComponent,
    NotificationBannerComponent,
    NewUpdateComponent,
  ],
  imports: [
    BrowserAnimationsModule,
    BrowserModule,
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatTooltipModule,
    MatCardModule,
    MatCardModule,
    MatCheckboxModule,
    MatDialogModule,
    MatDialogModule,
    MatIconModule,
    MatListModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatTableModule,
    ReactiveFormsModule,
    ScreenshotFeedbackModule,
    NewUpdateModule,
  ],
  providers: [NotificationBannerComponent],
})
export class WidgetsModule {}
