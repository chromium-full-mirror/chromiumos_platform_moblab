import {Pipe, PipeTransform} from '@angular/core';
import * as moment from 'moment';

@Pipe({name: 'msecFormatter'})
export class MsecFormatterPipe implements PipeTransform {
  transform(msec?: number | null): string {
    if (typeof msec === 'undefined' || msec === null) {
      return '--';
    }

    let mm = moment.duration(msec);
    return `
    ${mm.days() > 0 ? `${mm.days()} day(s)`: ''}
    ${mm.hours() > 0 ? ` ${mm.hours()} hour(s)` : ''} 
    ${mm.minutes() > 0 ? ` ${mm.minutes()} minute(s)` : ''} 
    ${mm.seconds() > 0 ? ` ${mm.seconds()} second(s)` : ''} 
    `;

  }
}
