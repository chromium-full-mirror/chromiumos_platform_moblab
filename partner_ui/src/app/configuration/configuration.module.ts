import {NgModule} from '@angular/core';
import {CommonModule} from "@angular/common";
import {WidgetsModule} from '../widgets/widgets.module';
import {MaterialModule} from '@angular/material';
import {ConfigurationComponent} from './configuration.component';

@NgModule({
  declarations: [
    ConfigurationComponent,
  ],
  exports: [
    ConfigurationComponent,
  ],
  providers: [
  ],
  imports: [
    MaterialModule.forRoot(),
    CommonModule,
    WidgetsModule,
  ]

})

export class ConfigurationModule { }