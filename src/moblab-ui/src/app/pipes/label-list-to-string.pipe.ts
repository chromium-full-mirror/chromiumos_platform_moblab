import {Pipe, PipeTransform} from '@angular/core';

@Pipe({name: 'labelListToString'})
export class LabelListToStringPipe implements PipeTransform {
  transform(
    labelList: string[],
    labelFilterSet: Set<string>,
    filterLabels: boolean
  ): any {
    return filterLabels
      ? labelList.filter(item => !labelFilterSet.has(item)).join(', ')
      : labelList;
  }
}
