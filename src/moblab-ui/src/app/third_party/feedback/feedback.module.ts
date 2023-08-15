import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {FeedbackDialogComponent} from './feedback-dialog/feedback-dialog.component';
import {FeedbackToolbarComponent} from './feedback-toolbar/feedback-toolbar.component';
import {FeedbackRectangleComponent} from './feedback-rectangle/feedback-rectangle.component';

import {MatDialogModule} from '@angular/material/dialog';
import {MatButtonModule} from '@angular/material/button';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatTooltipModule} from '@angular/material/tooltip';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';

import {FeedbackService} from './feedback.service';
import {FeedbackDirective} from './feedback.directive';

@NgModule({
  declarations: [
    FeedbackDialogComponent,
    FeedbackToolbarComponent,
    FeedbackRectangleComponent,
    FeedbackDirective,
  ],
  imports: [
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatTooltipModule,
    CommonModule,
    FormsModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
    ReactiveFormsModule,
  ],
  exports: [FeedbackDirective],
  providers: [FeedbackService],
})
export class FeedbackModule {}
