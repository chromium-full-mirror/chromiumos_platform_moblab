import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppComponent} from './app.component';
import {RunSuiteModule} from './run-suite/run-suite.module';
import {ServicesModule} from './services/services.module';

import {MaterialModule} from '@angular/material';
import {ManageDutModule} from './manage-duts/manage-dut.module';
import {ConfigurationModule} from './configuration/configuration.module';
import {AdvancedSettingsModule} from './advanced-settings/advanced-settings.module';


@NgModule({
  declarations: [
    AppComponent,
  ],
  imports: [
    MaterialModule.forRoot(),
    BrowserModule,
    RunSuiteModule,
    ManageDutModule,
    ConfigurationModule,
    AdvancedSettingsModule,
    ServicesModule.forRoot(),
  ],
  bootstrap: [AppComponent]
})

export class AppModule {
}

