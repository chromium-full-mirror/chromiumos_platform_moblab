import {Pipe, PipeTransform} from '@angular/core';

@Pipe({name: 'labelListToString'})
export class LabelListToStringPipe implements PipeTransform {
  transform(value: any, args?: any): any {
    return value.filter(item => !args.has(item)).join(', ');
  }
}
