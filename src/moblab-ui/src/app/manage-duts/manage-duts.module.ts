import { NgModule } from "@angular/core";
import { FormsModule } from "@angular/forms";
import {
  MatButtonModule,
  MatCheckboxModule,
  MatOptionModule,
  MatTableModule,
  MatTabsModule,
  MatSortModule
} from "@angular/material";
import { MatCardModule } from "@angular/material/card";
import { MatSelectModule } from "@angular/material/select";

import { PipesModule } from "app/pipes/pipes.module";

import { ServicesModule } from "../services/services.module";

import { EnrollmentComponent } from "./enrollment/enrollment.component";
import { FirmwareComponent } from "./firmware/firmware.component";
import { ManageDutsComponent } from "./manage-duts.component";
import { FlexLayoutModule } from "@angular/flex-layout";
import { WidgetsModule } from "../widgets/widgets.module";
import { CommonModule } from "@angular/common";

@NgModule({
  imports: [
    MatCheckboxModule,
    MatTabsModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatTableModule,
    MatOptionModule,
    MatSelectModule,
    PipesModule,
    ServicesModule,
    FlexLayoutModule,
    WidgetsModule,
    MatSortModule,
    CommonModule
  ],
  declarations: [ManageDutsComponent, EnrollmentComponent, FirmwareComponent],
  exports: [ManageDutsComponent]
})
export class ManageDutsModule {}
