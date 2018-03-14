import {Pipe} from '@angular/core';

@Pipe({
  name: 'mapToIterable'
})
// export class MapToIterable {
//   transform(dict: Object): Array<any> {
//     let a = [];
//     for (let key in dict) {
//       if (dict.hasOwnProperty(key)) {
//         a.push({key: key, val: dict[key]});
//       }
//     }
//     return a;
//   }
// }

export class MapToIterable {
  transform(value) {
    let result = [];

    if(value.entries) {
      for (var [key, value] of value.entries()) {
        result.push({ key, value });
      }
    } else {
      for(let key in value) {
        result.push({ key, value: value[key] });
      }
    }

    return result;
  }
}
