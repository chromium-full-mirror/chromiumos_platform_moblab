import { WidgetsModule } from './../widgets/widgets.module';
import { NgModule } from '@angular/core';
import { RunSuiteComponent } from './run-suite.component';
import { CtsRunComponent } from './custom-run-suite/cts-run/cts-run.component';
import { StorageQualComponent } from './custom-run-suite/storage-qual/storage-qual.component';
import { RouterModule } from '@angular/router';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTabsModule, MatButtonModule } from '@angular/material';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { BvtComponent } from './custom-run-suite/bvt/bvt.component';
import { MemoryQualComponent } from './custom-run-suite/memory-qual/memory-qual.component';
import { PowerComponent } from './custom-run-suite/power/power.component';
import { RunAnySuiteComponent } from './run-any-suite/run-any-suite.component';
import { BrowserModule } from '@angular/platform-browser';

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
  ]
})

export class RunSuiteModule { }
