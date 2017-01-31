import {NgModule} from '@angular/core';
import {MoblabSelector} from './moblab-selector.component'
import {CommonModule} from "@angular/common";

@NgModule({
  declarations: [
    MoblabSelector,
  ],
  exports: [
    MoblabSelector,
  ],
  imports: [
    CommonModule,
  ]
})

export class WidgetsModule { }

