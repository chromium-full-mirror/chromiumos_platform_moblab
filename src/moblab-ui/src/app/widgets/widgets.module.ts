import {NgModule} from '@angular/core';
import {MoblabSelectorComponent} from './moblab-selector/moblab-selector.component';
import {MoblabBuildSelectorComponent} from './moblab-build-selector/moblab-build-selector.component';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {MatSelectModule} from '@angular/material/select';
import {MatListModule} from '@angular/material/list';
import { MoblabRuntestSelectorComponent } from './moblab-runtest-selector/moblab-runtest-selector.component';
import { MatCardModule } from '@angular/material/card';

@NgModule({
  declarations: [
    MoblabSelectorComponent,
    MoblabBuildSelectorComponent,
    MoblabRuntestSelectorComponent,
  ],
  exports: [
    MoblabSelectorComponent,
    MoblabBuildSelectorComponent,
    MoblabRuntestSelectorComponent
  ],
  imports: [
    FormsModule,
    CommonModule,
    MatSelectModule,
    MatListModule,
    MatCardModule
  ]
})

export class WidgetsModule { }

