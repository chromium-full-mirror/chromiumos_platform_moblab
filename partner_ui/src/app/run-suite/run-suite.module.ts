import {NgModule} from '@angular/core';
import {CommonModule} from "@angular/common";
import {RunSuiteComponent} from './run-suite.component';
import {WidgetsModule} from '../widgets/widgets.module';
import {MaterialModule} from '@angular/material';

@NgModule({
  declarations: [
    RunSuiteComponent,
  ],
  exports: [
    RunSuiteComponent,
  ],
  providers: [
  ],
  imports: [
    MaterialModule.forRoot(),
    CommonModule,
    WidgetsModule,
  ]

})

export class RunSuiteModule { }
