
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ViewJobsComponent } from './view-jobs/view-jobs.component';
import { RunSuiteComponent } from './run-suite/run-suite.component';
import { CtsRunComponent } from './run-suite/custom-run-suite/cts-run/cts-run.component';
import { APP_BASE_HREF } from '@angular/common';
import { ManageDutsComponent } from './manage-duts/manage-duts.component';
import { StorageQualComponent } from './run-suite/custom-run-suite/storage-qual/storage-qual.component';
import { ConfigurationComponent } from './configuration/configuration.component';
import { MobmonitorComponent } from './mobmonitor/mobmonitor.component';

const routes: Routes = [
  { path: 'view_jobs', component: ViewJobsComponent },
  { path: 'run_tests', component: RunSuiteComponent,
    children: [
      {path: 'cts', component: CtsRunComponent},
      {path: 'storagequal', component: StorageQualComponent},
      {path: 'memoryqual', component: StorageQualComponent},
      {path: 'bvtqual', component: StorageQualComponent},
      {path: 'powerqual', component: StorageQualComponent},
      {path: 'runsuite', component: StorageQualComponent},
    ]
  },
  { path: 'manage_dut', component: ManageDutsComponent },
  { path: 'config', component: ConfigurationComponent },
  { path: 'mobmonitor', component: MobmonitorComponent },
  { path: 'advanced', component: ViewJobsComponent },
  { path: 'report_problem', component: ViewJobsComponent },
  { path: '**', component: ViewJobsComponent },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ],
  providers: [ { provide: APP_BASE_HREF, useValue: '/' } ]
})

export class AppRoutingModule {
}
