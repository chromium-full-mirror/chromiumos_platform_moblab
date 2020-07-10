import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {BrowserModule} from '@angular/platform-browser';
import {CommonModule} from '@angular/common';
import {ConfirmationDialog} from './reboot-button/reboot-button';
import {FlexLayoutModule} from '@angular/flex-layout';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatDialogModule} from '@angular/material/dialog';
import {MatIconModule} from '@angular/material/icon';
import {MatListModule} from '@angular/material/list';
import {MatSelectModule} from '@angular/material/select';
import {MatTableModule} from '@angular/material/table';
import {NgModule} from '@angular/core';

import {KeyValTableComponent} from './keyval-table/keyval-table.component'
import {RebootButtonComponent} from './reboot-button/reboot-button';
import {TableHeaderSelectorComponent} from './table-header-selector/table-header-selector.component';

import {FeedbackComponent, SubmissionResultDialog} from './feedback/feedback.component';
import {FeedbackModule as ScreenshotFeedbackModule} from '../third_party/feedback/feedback.module';


@NgModule({
  declarations: [
    ConfirmationDialog,
    FeedbackComponent,
    KeyValTableComponent,
    RebootButtonComponent,
    SubmissionResultDialog,
    TableHeaderSelectorComponent
  ],
  exports: [
    FeedbackComponent,
    KeyValTableComponent,
    RebootButtonComponent,
    TableHeaderSelectorComponent
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
    MatSelectModule,
    MatTableModule,
    ReactiveFormsModule,
    ScreenshotFeedbackModule,
  ]
})
export class WidgetsModule {}
