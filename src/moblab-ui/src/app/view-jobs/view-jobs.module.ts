import { NgModule } from "@angular/core";
import {
  MatButtonModule,
  MatCheckboxModule,
  MatTableModule,
  MatListModule,
  MatSortModule,
  MatChipsModule,
  MatSnackBarModule
} from "@angular/material";
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatCardModule } from "@angular/material/card";
import { MatSelectModule } from "@angular/material/select";
import { MatIconModule } from "@angular/material/icon";
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatExpansionModule } from '@angular/material/expansion';
import { CommonModule } from "@angular/common";

import { ViewJobsComponent } from "./view-jobs.component";
import { WidgetsModule } from "../widgets/widgets.module";

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
    MatProgressSpinnerModule,
    MatSelectModule,
    MatSnackBarModule,
    MatSortModule,
    MatTableModule,
    ReactiveFormsModule,
    WidgetsModule,
  ],
  declarations: [ViewJobsComponent],
  exports: [ViewJobsComponent]
})
export class ViewJobsModule {}
