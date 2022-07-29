import {CommonModule} from '@angular/common';
import {NgModule} from '@angular/core';
import {MsecFormatterPipe} from './msec-formatter.pipe';

import {LabelListToStringPipe} from './label-list-to-string.pipe';

@NgModule({
  imports: [CommonModule],
  declarations: [
    LabelListToStringPipe,
    MsecFormatterPipe,
  ],
  exports: [
    LabelListToStringPipe,
    MsecFormatterPipe,
  ],
})
export class PipesModule {}
