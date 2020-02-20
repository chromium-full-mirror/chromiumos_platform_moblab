import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { MatCardModule } from "@angular/material/card";
import { MatListModule } from "@angular/material/list";
import { MatSelectModule } from "@angular/material/select";

import { MoblabBuildSelectorComponent } from "./moblab-build-selector/moblab-build-selector.component";
import { MoblabRuntestSelectorComponent } from "./moblab-runtest-selector/moblab-runtest-selector.component";
import { MoblabSelectorComponent } from "./moblab-selector/moblab-selector.component";
import { TableHeaderSelectorComponent } from "./table-header-selector/table-header-selector.component";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { FlexLayoutModule } from "@angular/flex-layout";

@NgModule({
  declarations: [
    MoblabSelectorComponent,
    MoblabBuildSelectorComponent,
    MoblabRuntestSelectorComponent,
    TableHeaderSelectorComponent
  ],
  exports: [
    MoblabSelectorComponent,
    MoblabBuildSelectorComponent,
    MoblabRuntestSelectorComponent,
    TableHeaderSelectorComponent
  ],
  imports: [
    FormsModule,
    CommonModule,
    MatSelectModule,
    MatListModule,
    MatCardModule,
    MatCheckboxModule,
    FlexLayoutModule
  ]
})
export class WidgetsModule {}
