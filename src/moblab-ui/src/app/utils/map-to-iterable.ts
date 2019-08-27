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
    const result = [];

    // if(value.entries) {
    //   for (const [key, value] of value.entries()) {
    //     result.push({ key, value });
    //   }
    // } else {
    //   for(const key in value) {
    //     result.push({ key, value: value[key] });
    //   }
    // }

    return result;
  }
}
