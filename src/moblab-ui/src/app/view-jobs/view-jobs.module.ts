import {
  MatButtonModule,
  MatCheckboxModule,
  MatTableModule,
  MatListModule,
  MatSortModule,
  MatChipsModule,
  MatSnackBarModule
} from '@angular/material';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {CommonModule} from '@angular/common';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatCardModule} from '@angular/material/card';
import {MatExpansionModule} from '@angular/material/expansion';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatPaginatorModule} from '@angular/material/paginator';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatSelectModule} from '@angular/material/select';
import {NgModule} from '@angular/core';
import {RouterModule} from '@angular/router';

import {JobActionComponent} from './job-action/job-action.component';
import {ViewJobsComponent} from './view-jobs.component';
import {WidgetsModule} from '../widgets/widgets.module';


@NgModule({
  imports: [
    BrowserAnimationsModule,
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatChipsModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatSnackBarModule,
    MatSortModule,
    MatTableModule,
    ReactiveFormsModule,
    RouterModule,
    WidgetsModule,
  ],
  declarations: [JobActionComponent, ViewJobsComponent],
  exports: [ViewJobsComponent]
})
export class ViewJobsModule {}
