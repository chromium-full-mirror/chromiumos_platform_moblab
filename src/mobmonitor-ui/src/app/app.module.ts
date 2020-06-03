import {BrowserModule} from '@angular/platform-browser';
import {HttpClientModule} from '@angular/common/http';
import {NgModule} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {MatCardModule} from '@angular/material/card';
import {MatButtonModule} from '@angular/material/button';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatDialogModule} from '@angular/material/dialog';
import {MatInputModule} from '@angular/material/input';
import {MatProgressBarModule} from '@angular/material/progress-bar';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatGridListModule} from '@angular/material/grid-list';

import {AppComponent} from './app.component';
import {HealthChecksComponent} from './health-checks/health-checks.component';
import {MobmonitorRpcService} from './services/mobmonitor-rpc.service';
import {ErrorDisplayService} from './services/error-display.service';
import {ActionsComponent} from './actions/actions.component';
import {ActionsParamDialogComponent} from './services/actions-param-dialog/actions-param-dialog.component';
import {ErrorDisplayDialogComponent} from './services/error-display-dialog/error-display-dialog.component';
import {DiagnosticsComponent} from './diagnostics/diagnostics.component';

@NgModule({
  declarations: [
    AppComponent,
    HealthChecksComponent,
    ActionsComponent,
    ActionsParamDialogComponent,
    ErrorDisplayDialogComponent,
    DiagnosticsComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDialogModule,
    MatInputModule,
    MatProgressBarModule,
    BrowserAnimationsModule,
    MatGridListModule
  ],
  entryComponents: [ActionsParamDialogComponent, ErrorDisplayDialogComponent],
  providers: [MobmonitorRpcService, ErrorDisplayService],
  bootstrap: [AppComponent]
})
export class AppModule {}
