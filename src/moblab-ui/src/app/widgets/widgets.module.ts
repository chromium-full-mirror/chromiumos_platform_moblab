import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {BrowserModule} from '@angular/platform-browser';
import {CommonModule} from '@angular/common';
import {ConfirmationDialog} from './confirmation-dialog/confirmation-dialog.component';
import {FlexLayoutModule} from '@angular/flex-layout';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatDialogModule} from '@angular/material/dialog';
import {MatIconModule} from '@angular/material/icon';
import {MatListModule} from '@angular/material/list';
import {MatProgressBarModule} from '@angular/material/progress-bar';
import {MatSelectModule} from '@angular/material/select';
import {MatTableModule} from '@angular/material/table';
import {NgModule} from '@angular/core';

import {KeyValTableComponent} from './keyval-table/keyval-table.component';
import {LoadingOverlayComponent} from './loading-overlay/loading-overlay.component';
import {RebootButtonComponent} from './reboot-button/reboot-button.component';
import {TableHeaderSelectorComponent} from './table-header-selector/table-header-selector.component';
import {UpdateButtonComponent} from './update-button/update-button.component';

import {FeedbackComponent, SubmissionResultDialog} from './feedback/feedback.component';
import {FeedbackModule as ScreenshotFeedbackModule} from '../third_party/feedback/feedback.module';


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
  ],
  exports: [
    FeedbackComponent,
    KeyValTableComponent,
    LoadingOverlayComponent,
    RebootButtonComponent,
    TableHeaderSelectorComponent,
    UpdateButtonComponent,
  ],
  imports: [
    BrowserAnimationsModule,
    BrowserModule,
    CommonModule,
    FlexLayoutModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatCardModule,
    MatCheckboxModule,
    MatDialogModule,
    MatDialogModule,
    MatIconModule,
    MatListModule,
    MatProgressBarModule,
    MatSelectModule,
    MatTableModule,
    ReactiveFormsModule,
    ScreenshotFeedbackModule,
  ]
})
export class WidgetsModule {}
