import {NgModule} from '@angular/core';
import {CommonModule} from "@angular/common";
import {WidgetsModule} from '../widgets/widgets.module';
import {MaterialModule} from '@angular/material';
import {ConfigurationComponent} from './configuration.component';
import {FormsModule} from '@angular/forms';
import { FileSelectDirective } from 'ng2-file-upload';

@NgModule({
  declarations: [
    ConfigurationComponent,
    FileSelectDirective
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
    FormsModule,
  ]
})

export class ConfigurationModule { }