import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { MatCardModule } from "@angular/material/card";
import { MatListModule } from "@angular/material/list";
import { MatSelectModule } from "@angular/material/select";
import { MatTableModule } from '@angular/material';

import { KeyValTableComponent } from "./keyval-table/keyval-table.component"
import { MoblabBuildSelectorComponent } from "./moblab-build-selector/moblab-build-selector.component";
import { MoblabRuntestSelectorComponent } from "./moblab-runtest-selector/moblab-runtest-selector.component";
import { MoblabSelectorComponent } from "./moblab-selector/moblab-selector.component";
import { TableHeaderSelectorComponent } from "./table-header-selector/table-header-selector.component";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { FlexLayoutModule } from "@angular/flex-layout";

@NgModule({
  declarations: [
    KeyValTableComponent,
    MoblabSelectorComponent,
    MoblabBuildSelectorComponent,
    MoblabRuntestSelectorComponent,
    TableHeaderSelectorComponent
  ],
  exports: [
    KeyValTableComponent,
    MoblabSelectorComponent,
    MoblabBuildSelectorComponent,
    MoblabRuntestSelectorComponent,
    TableHeaderSelectorComponent
  ],
  imports: [
    CommonModule,
    FlexLayoutModule,
    FormsModule,
    MatCardModule,
    MatCheckboxModule,
    MatListModule,
    MatSelectModule,
    MatTableModule,
    ReactiveFormsModule
  ]
})
export class WidgetsModule {}
