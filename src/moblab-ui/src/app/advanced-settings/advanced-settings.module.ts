import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {WidgetsModule} from '../widgets/widgets.module';
import {AdvancedSettingsComponent} from './advanced-settings.component';
import {FormsModule} from '@angular/forms';
import {UtilsModule} from '../utils/utils.module';

import {MatCardModule} from '@angular/material/card';


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
    CommonModule,
    WidgetsModule,
    FormsModule,
    UtilsModule,
    MatCardModule,
  ]

})

export class AdvancedSettingsModule { }
