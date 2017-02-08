import {NgModule} from '@angular/core';
import {CommonModule} from "@angular/common";
import {WidgetsModule} from '../widgets/widgets.module';
import {MaterialModule} from '@angular/material';
import {AdvancedSettingsComponent} from './advanced-settings.component';

@NgModule({
  declarations: [
    AdvancedSettingsComponent,
  ],
  exports: [
    AdvancedSettingsComponent,
  ],
  providers: [
  ],
  imports: [
    MaterialModule.forRoot(),
    CommonModule,
    WidgetsModule,
  ]

})

export class AdvancedSettingsModule { }