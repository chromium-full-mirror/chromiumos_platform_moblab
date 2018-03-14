import {NgModule} from '@angular/core';
import {CommonModule} from "@angular/common";
import {WidgetsModule} from '../widgets/widgets.module';
import {MaterialModule} from '@angular/material';
import {AdvancedSettingsComponent} from './advanced-settings.component';
import {FormsModule} from '@angular/forms';
import {UtilsModule} from '../utils/utils.module';


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
    FormsModule,
    UtilsModule,
  ]

})

export class AdvancedSettingsModule { }