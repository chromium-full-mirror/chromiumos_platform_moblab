import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {BrowserModule} from '@angular/platform-browser';
import {CommonModule} from '@angular/common';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {HttpClientModule} from '@angular/common/http';
import {LayoutModule} from '@angular/cdk/layout';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatChipsModule} from '@angular/material/chips';
import {MatDividerModule} from '@angular/material/divider';
import {MatExpansionModule} from '@angular/material/expansion';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatListModule} from '@angular/material/list';
import {MatMenuModule} from '@angular/material/menu';
import {MatPaginatorModule} from '@angular/material/paginator';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatSelectModule} from '@angular/material/select';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatTableModule} from '@angular/material/table';
import {MatTabsModule} from '@angular/material/tabs';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatTooltipModule} from '@angular/material/tooltip';
import {NgModule} from '@angular/core';
import {RouterModule} from '@angular/router';
import {MatProgressBarModule} from '@angular/material/progress-bar';

import {AdvancedSettingsComponent} from './advanced-settings/advanced-settings.component';
import {AppComponent} from './app.component';
import {AppRoutingModule} from './app-routing.module';
import {AppSidebarComponent} from './app-sidebar/app-sidebar.component';
import {ConfigurationComponent} from './configuration/configuration.component';
import {DutDetailModule} from './dut-detail/dut-detail.module';
import {JobDetailModule} from './job-detail/job-detail.module';
import {ManageDutsModule} from './manage-duts/manage-duts.module';
import {MobmonitorComponent} from './mobmonitor/mobmonitor.component';
import {MobmonitorPipe} from './mobmonitor/mobmonitor.component';
import {PipesModule} from './pipes/pipes.module';
import {RunSuiteModule} from './run-suite/run-suite.module';
import {ServicesModule} from './services/services.module';
import {ViewJobsModule} from './view-jobs/view-jobs.module';
import {WidgetsModule} from './widgets/widgets.module';
import {HealthCheckComponent} from './health-check/health-check.component';
import {AboutComponent} from './about/about.component';

@NgModule({
  declarations: [
    AdvancedSettingsComponent,
    AppComponent,
    AppSidebarComponent,
    ConfigurationComponent,
    MobmonitorComponent,
    MobmonitorPipe,
    HealthCheckComponent,
    AboutComponent,
  ],
  imports: [
    AppRoutingModule,
    BrowserAnimationsModule,
    BrowserModule,
    CommonModule,
    DutDetailModule,
    FormsModule,
    HttpClientModule,
    JobDetailModule,
    LayoutModule,
    ManageDutsModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatChipsModule,
    MatDividerModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatMenuModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatProgressBarModule,
    MatSelectModule,
    MatSidenavModule,
    MatTableModule,
    MatTabsModule,
    MatToolbarModule,
    MatTooltipModule,
    PipesModule,
    ReactiveFormsModule,
    RouterModule,
    RunSuiteModule,
    ServicesModule.forRoot(),
    ViewJobsModule,
    WidgetsModule,
  ],
  exports: [
    AppRoutingModule,
    MatCardModule,
    MatMenuModule,
    MatTableModule,
    RouterModule,
    RunSuiteModule,
    WidgetsModule,
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
