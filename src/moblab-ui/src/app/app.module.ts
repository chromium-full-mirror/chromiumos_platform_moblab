
import {LayoutModule} from '@angular/cdk/layout';
import {CommonModule} from '@angular/common';
import {HttpClientModule} from '@angular/common/http';
import {NgModule} from '@angular/core';
import {FlexLayoutModule} from '@angular/flex-layout';
import {FormsModule} from '@angular/forms';
import {MatChipsModule, MatTabsModule} from '@angular/material';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatListModule} from '@angular/material/list';
import {MatMenuModule} from '@angular/material/menu';
import {MatSelectModule} from '@angular/material/select';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatTableModule} from '@angular/material/table';
import {MatToolbarModule} from '@angular/material/toolbar';
import {BrowserModule} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterModule} from '@angular/router';
import {FeedbackModule} from 'ng-feedback';

import {AppRoutingModule} from './app-routing.module';
import {AppSidebarComponent} from './app-sidebar/app-sidebar.component';
import {AppComponent} from './app.component';
import {ConfigurationComponent} from './configuration/configuration.component';
import {ManageDutsComponent} from './manage-duts/manage-duts.component';
import {ManageDutsModule} from './manage-duts/manage-duts.module';
import {MobmonitorComponent} from './mobmonitor/mobmonitor.component';
import {MobmonitorPipe} from './mobmonitor/mobmonitor.component';
import {PipesModule} from './pipes/pipes.module';
import {RunSuiteModule} from './run-suite/run-suite.module';
import {ServicesModule} from './services/services.module';
import {ViewJobsComponent} from './view-jobs/view-jobs.component';
import {WidgetsModule} from './widgets/widgets.module';
import { AdvancedSettingsComponent } from './advanced-settings/advanced-settings.component';

@NgModule({
   declarations: [
      AppComponent,
      AppSidebarComponent,
      ViewJobsComponent,
      ConfigurationComponent,
      MobmonitorComponent,
      MobmonitorPipe,
      AdvancedSettingsComponent
   ],
   imports: [
      MatSnackBarModule,
      BrowserModule,
      BrowserAnimationsModule,
      ServicesModule.forRoot(),
      MatIconModule,
      MatListModule,
      MatMenuModule,
      MatSidenavModule,
      MatToolbarModule,
      MatCardModule,
      BrowserAnimationsModule,
      MatFormFieldModule,
      MatInputModule,
      MatButtonModule,
      LayoutModule,
      CommonModule,
      AppRoutingModule,
      RouterModule,
      MatTabsModule,
      WidgetsModule,
      MatTableModule,
      MatCheckboxModule,
      HttpClientModule,
      FlexLayoutModule,
      FormsModule,
      RunSuiteModule,
      MatChipsModule,
      FeedbackModule,
      MatSelectModule,
      PipesModule,
      ManageDutsModule
   ],
   exports: [
      WidgetsModule,
      AppRoutingModule,
      RouterModule,
      MatCardModule,
      MatTableModule,
      MatMenuModule,
      RunSuiteModule
   ],
   bootstrap: [
      AppComponent
   ]
})

export class AppModule {
}
