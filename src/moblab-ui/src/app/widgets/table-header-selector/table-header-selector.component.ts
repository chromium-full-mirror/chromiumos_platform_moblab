import { Component, OnInit, EventEmitter, Input, Output } from "@angular/core";
import { emit } from "cluster";

@Component({
  selector: "app-table-header-selector",
  templateUrl: "./table-header-selector.component.html",
  styleUrls: ["./table-header-selector.component.scss"]
})
export class TableHeaderSelectorComponent implements OnInit {
  selectValue: string = undefined;
  checkboxState = false;

  @Input() options: string[];
  @Output() update = new EventEmitter();

  standardOptions = ["All", "None"];

  constructor() {}

  ngOnInit() {}

  selectionChange() {
    this.update.emit({ selection: this.selectValue });
    if (this.selectValue == this.standardOptions[0]) {
      this.checkboxState = true;
    } else if (this.selectValue == this.standardOptions[0]) {
      this.checkboxState == false;
    } else {
      this.checkboxState = true;
    }
    this.selectValue = undefined;
  }

  checkboxChange() {
    this.update.emit({
      selection: this.checkboxState
        ? this.standardOptions[0]
        : this.standardOptions[1]
    });
  }
}
