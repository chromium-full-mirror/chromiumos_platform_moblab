import {CommonModule} from '@angular/common';
import {NgModule} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatTableModule} from '@angular/material/table';
import {MatCardModule} from '@angular/material/card';
import {MatDividerModule} from '@angular/material/divider';
import {MatExpansionModule} from '@angular/material/expansion';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {PipesModule} from '../pipes/pipes.module';

import {JobDetailComponent} from './job-detail.component';

import {ViewJobsModule} from '../view-jobs/view-jobs.module';
import {WidgetsModule} from '../widgets/widgets.module';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatDividerModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatTableModule,
    ReactiveFormsModule,
    ViewJobsModule,
    WidgetsModule,
    PipesModule,
  ],
  declarations: [JobDetailComponent],
  exports: [JobDetailComponent],
})
export class JobDetailModule {}
