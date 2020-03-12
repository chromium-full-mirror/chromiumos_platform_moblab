import {APP_BASE_HREF} from '@angular/common';
import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';

import {ConfigurationComponent} from './configuration/configuration.component';
import {CtsRunComponent} from './run-suite/custom-run-suite/cts-run/cts-run.component';
import {DutDetailComponent} from './dut-detail/dut-detail.component';
import {JobDetailComponent} from './job-detail/job-detail.component';
import {ManageDutsComponent} from './manage-duts/manage-duts.component';
import {MobmonitorComponent} from './mobmonitor/mobmonitor.component';
import {RunSuiteComponent} from './run-suite/run-suite.component';
import {StorageQualComponent} from './run-suite/custom-run-suite/storage-qual/storage-qual.component';
import {ViewJobsComponent} from './view-jobs/view-jobs.component';

const routes: Routes = [
  {path: 'view_jobs', component: ViewJobsComponent},
  {path: 'job_detail', component: JobDetailComponent},
  {path: 'job_detail/:job_id', component: JobDetailComponent},
  {path: 'dut_detail', component: DutDetailComponent},
  {path: 'dut_detail/:dut_ip', component: DutDetailComponent},
  {
    path: 'run_tests',
    component: RunSuiteComponent,
    children: [
      {path: 'cts', component: CtsRunComponent},
      {path: 'storagequal', component: StorageQualComponent},
      {path: 'memoryqual', component: StorageQualComponent},
      {path: 'bvtqual', component: StorageQualComponent},
      {path: 'powerqual', component: StorageQualComponent},
      {path: 'runsuite', component: StorageQualComponent},
    ]
  },
  {path: 'manage_dut', component: ManageDutsComponent},
  {path: 'config', component: ConfigurationComponent},
  {path: 'mobmonitor', component: MobmonitorComponent},
  {path: 'advanced', component: ViewJobsComponent},
  {path: 'report_problem', component: ViewJobsComponent},
  {path: '**', component: ViewJobsComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { enableTracing: true, useHash: true })],
  exports: [RouterModule],
  providers: [{provide: APP_BASE_HREF, useValue: ''}]
})

export class AppRoutingModule {
}
