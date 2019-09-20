import {CommonModule} from '@angular/common';
import {NgModule} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {MatCardModule} from '@angular/material/card';
import {MatListModule} from '@angular/material/list';
import {MatSelectModule} from '@angular/material/select';

import {MoblabBuildSelectorComponent} from './moblab-build-selector/moblab-build-selector.component';
import {MoblabRuntestSelectorComponent} from './moblab-runtest-selector/moblab-runtest-selector.component';
import {MoblabSelectorComponent} from './moblab-selector/moblab-selector.component';

@NgModule({
  declarations: [
    MoblabSelectorComponent,
    MoblabBuildSelectorComponent,
    MoblabRuntestSelectorComponent,
  ],
  exports: [
    MoblabSelectorComponent, MoblabBuildSelectorComponent,
    MoblabRuntestSelectorComponent
  ],
  imports: [
    FormsModule, CommonModule, MatSelectModule, MatListModule, MatCardModule
  ]
})

export class WidgetsModule {
}
