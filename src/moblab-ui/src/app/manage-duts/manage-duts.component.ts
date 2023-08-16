import {Component, OnInit} from '@angular/core';

@Component({
  selector: 'app-manage-duts',
  templateUrl: './manage-duts.component.html',
  styleUrls: ['/manage-duts.component.scss'],
})
export class ManageDutsComponent implements OnInit {
  selectedTabIndex = 0;

  constructor() {}

  ngOnInit() {}

  tabChanged() {
    console.log(this.selectedTabIndex);
  }
}
