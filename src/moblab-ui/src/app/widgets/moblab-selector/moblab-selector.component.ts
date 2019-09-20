import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChange, SimpleChanges, ViewChild} from '@angular/core';


@Component({
  selector: 'app-moblab-selector',
  templateUrl: './moblab-selector.component.html',
  styleUrls: ['./moblab-selector.component.scss'],
})

export class MoblabSelectorComponent implements OnChanges, OnInit {
  @Input() title: string;
  @Input() placeholder: string;
  @Input() options: string[];
  @Input() isShown: boolean;
  @Input() autoselect = true;

  @Output() update = new EventEmitter();
  @Output() selected: string = null;

  _options: string[];
  private _isShown: boolean;

  ngOnChanges(changes: SimpleChanges) {
    if (changes.options) {
      this._options = changes.options.currentValue;
      this.autoSelectedSingleOption();
    }
  }

  autoSelectedSingleOption() {
    // If the drop down only has one item - auto select it.
    if (this.autoselect && this._options.length == 1) {
      this.selected = this._options[0];
      this.update.emit({value: this.selected});
    }
  }

  ngOnInit() {
    this._options = this.options;
    this._isShown = this.isShown;
    this.autoSelectedSingleOption();
  }

  onChange(event): void {
    this.update.emit(event);
  }

  getSelectedValue(): string {
    if (!this.isShown) {
      return null;
    } else {
      return this.selected;
    }
  }
}
