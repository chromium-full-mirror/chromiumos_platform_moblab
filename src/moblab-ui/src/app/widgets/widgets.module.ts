import {CommonModule} from '@angular/common';
import {FlexLayoutModule} from '@angular/flex-layout';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatListModule} from '@angular/material/list';
import {MatSelectModule} from '@angular/material/select';
import {MatTableModule} from '@angular/material/table';
import {NgModule} from '@angular/core';

import {KeyValTableComponent} from './keyval-table/keyval-table.component'
import {TableHeaderSelectorComponent} from './table-header-selector/table-header-selector.component';

@NgModule({
  declarations: [
    KeyValTableComponent,
    TableHeaderSelectorComponent
  ],
  exports: [
    KeyValTableComponent,
    TableHeaderSelectorComponent
  ],
  imports: [
    CommonModule,
    FlexLayoutModule,
    FormsModule,
    MatCardModule,
    MatCheckboxModule,
    MatListModule,
    MatSelectModule,
    MatTableModule,
    ReactiveFormsModule
  ]
})
export class WidgetsModule {}
