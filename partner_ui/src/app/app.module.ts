import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { RunSuiteModule } from './run-suite/run-suite.module';
import { ServicesModule} from './services/services.module';


@NgModule({
  declarations: [
    AppComponent,
  ],
  imports: [
    BrowserModule,
    RunSuiteModule,
    ServicesModule.forRoot(),
  ],
  bootstrap: [AppComponent]
})

export class AppModule { }

