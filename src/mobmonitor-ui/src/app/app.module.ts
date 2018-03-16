import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { MatCardModule, MatButtonModule, MatProgressSpinnerModule, MatSnackBarModule } from '@angular/material';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { AppComponent } from './app.component';
import { HealthChecksComponent } from './health-checks/health-checks.component';
import { MobmonitorRpcService } from './services/mobmonitor-rpc.service';
import { ActionsComponent } from './actions/actions.component';


@NgModule({
  declarations: [
    AppComponent,
    HealthChecksComponent,
    ActionsComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    MatCardModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    BrowserAnimationsModule
  ],
  providers: [MobmonitorRpcService],
  bootstrap: [AppComponent]
})
export class AppModule { }
