import {NgModule} from '@angular/core';
import {CommonModule} from "@angular/common";
import {RunSuiteComponent} from './run-suite.component';
import {WidgetsModule} from '../widgets/widgets.module';

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
    CommonModule,
    WidgetsModule,
  ]

})

export class RunSuiteModule { }
