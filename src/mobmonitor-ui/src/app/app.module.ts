import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatCardModule, MatButtonModule, MatProgressSpinnerModule,
         MatSnackBarModule, MatDialogModule, MatInputModule } from '@angular/material';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { AppComponent } from './app.component';
import { HealthChecksComponent } from './health-checks/health-checks.component';
import { MobmonitorRpcService } from './services/mobmonitor-rpc.service';
import { ActionsComponent } from './actions/actions.component';
import { ActionsParamDialogComponent } from './services/actions-param-dialog/actions-param-dialog.component';


@NgModule({
  declarations: [
    AppComponent,
    HealthChecksComponent,
    ActionsComponent,
    ActionsParamDialogComponent
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
    BrowserAnimationsModule
  ],
  entryComponents: [
    ActionsParamDialogComponent
  ],
  providers: [MobmonitorRpcService],
  bootstrap: [AppComponent]
})
export class AppModule { }
