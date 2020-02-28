import { NgModule } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { MatButtonModule } from "@angular/material/button";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatTabsModule } from "@angular/material/tabs";
import { MatSortModule } from "@angular/material/sort";
import { MatTableModule } from "@angular/material/table";
import { MatCardModule } from "@angular/material/card";

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
    CommonModule
    FlexLayoutModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatSortModule,
    MatTableModule,
    MatTabsModule,
    PipesModule,
    ServicesModule,
    WidgetsModule,
  ],
  declarations: [
    EnrollmentComponent,
    FirmwareComponent
    ManageDutsComponent,
  ],
  exports: [ManageDutsComponent]
})
export class ManageDutsModule {}
