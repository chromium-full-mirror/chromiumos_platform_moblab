import {Component} from '@angular/core';
import {MatTableDataSource} from '@angular/material/table';

export interface KeyVal {
  key: string;
  value: string;
}

@Component({
  selector: 'app-keyval-table',
  templateUrl: './keyval-table.component.html',
  styleUrls: ['./keyval-table.component.scss'],
})
export class KeyValTableComponent {
  infoTable = new MatTableDataSource<KeyVal>();
  tableColumns: string[] = ['key', 'value'];

  loadRows(keyvals: string[][]) {
    const infoRows: KeyVal[] = [];
    for (const entry of keyvals) {
      infoRows.push({
        key: entry[0],
        value: entry[1],
      });
    }
    this.infoTable = new MatTableDataSource<KeyVal>(infoRows);
  }

  isEmpty(): boolean {
    return !this.infoTable.data.length;
  }
}
