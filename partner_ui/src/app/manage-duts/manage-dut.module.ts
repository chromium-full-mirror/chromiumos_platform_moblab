import {NgModule} from '@angular/core';
import {CommonModule} from "@angular/common";
import {WidgetsModule} from '../widgets/widgets.module';
import {MaterialModule} from '@angular/material';
import {ManageDutComponent} from './manage-dut.component';

@NgModule({
  declarations: [
    ManageDutComponent,
  ],
  exports: [
    ManageDutComponent,
  ],
  providers: [
  ],
  imports: [
    MaterialModule.forRoot(),
    CommonModule,
    WidgetsModule,
  ]

})

export class ManageDutModule { }