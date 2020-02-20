import { NgModule } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { MatButtonModule } from "@angular/material/button";
import { MatTabsModule } from "@angular/material/tabs";
import { MatCardModule } from "@angular/material/card";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { BrowserModule } from "@angular/platform-browser";
import { RouterModule } from "@angular/router";

import { WidgetsModule } from "./../widgets/widgets.module";
import { BvtComponent } from "./custom-run-suite/bvt/bvt.component";
import { CtsRunComponent } from "./custom-run-suite/cts-run/cts-run.component";
import { MemoryQualComponent } from "./custom-run-suite/memory-qual/memory-qual.component";
import { PowerComponent } from "./custom-run-suite/power/power.component";
import { StorageQualComponent } from "./custom-run-suite/storage-qual/storage-qual.component";
import { RunAnySuiteComponent } from "./run-any-suite/run-any-suite.component";
import { MatInputModule } from "@angular/material/input";
import { MatIconModule } from "@angular/material/icon";
import { RunSuiteComponent } from "./run-suite.component";

@NgModule({
  declarations: [
    RunSuiteComponent,
    CtsRunComponent,
    StorageQualComponent,
    BvtComponent,
    MemoryQualComponent,
    PowerComponent,
    RunAnySuiteComponent
  ],
  exports: [
    RunSuiteComponent,
    CtsRunComponent,
    StorageQualComponent,
    BvtComponent,
    MemoryQualComponent,
    PowerComponent,
    RunAnySuiteComponent
  ],
  imports: [
    BrowserModule,
    RouterModule,
    WidgetsModule,
    MatCheckboxModule,
    MatTabsModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatInputModule,
    MatIconModule,
    WidgetsModule
  ]
})
export class RunSuiteModule {}
