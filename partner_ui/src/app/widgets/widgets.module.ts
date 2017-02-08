import {NgModule} from '@angular/core';
import {MoblabSelector} from './moblab-selector.component'
import {CommonModule} from "@angular/common";
import {MaterialModule} from '@angular/material';
import {FormsModule} from '@angular/forms';

@NgModule({
  declarations: [
    MoblabSelector,
  ],
  exports: [
    MoblabSelector,
  ],
  imports: [
    MaterialModule.forRoot(),
    FormsModule,
    CommonModule,
  ]
})

export class WidgetsModule { }

