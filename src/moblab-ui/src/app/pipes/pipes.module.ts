import {CommonModule} from '@angular/common';
import {NgModule} from '@angular/core';

import {LabelListToStringPipe} from './label-list-to-string.pipe';

@NgModule({
  imports: [CommonModule],
  declarations: [LabelListToStringPipe],
  exports: [LabelListToStringPipe],
})
export class PipesModule {}
