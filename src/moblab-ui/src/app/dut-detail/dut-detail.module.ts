import {CommonModule} from '@angular/common';
import {NgModule} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatDividerModule} from '@angular/material/divider';
import {MatExpansionModule} from '@angular/material/expansion';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import {MatPaginatorModule} from '@angular/material/paginator';
import {MatTableModule} from '@angular/material/table';

import {DutDetailComponent} from './dut-detail.component';
import {DutTaskTableComponent} from './dut_task_table/dut_task_table.component';
import {MatIconModule} from '@angular/material/icon';
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
    MatPaginatorModule,
    MatTableModule,
    ReactiveFormsModule,
    ViewJobsModule,
    WidgetsModule,
  ],
  declarations: [DutDetailComponent, DutTaskTableComponent],
  exports: [DutDetailComponent],
})
export class DutDetailModule {}
