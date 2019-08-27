import { Component, Input, Output, EventEmitter, ViewChild, OnChanges, SimpleChanges, SimpleChange, OnInit } from '@angular/core';


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

  @Output() update = new EventEmitter();
  @Output() selectedValue: string = null;

  _options: string[];
  private _isShown: boolean;

  ngOnChanges(changes: SimpleChanges) {
    if (changes.options) {
      this._options = changes.options.currentValue;
    }
  }

  ngOnInit() {
    this._options = this.options;
    this._isShown = this._isShown;
  }

  onChange(event): void {
   this.selectedValue = event;
   this.update.emit({value: event});
  }

  getSelectedValue(): string {
    if (!this.isShown) {
      return null;
    } else {
      return this.selectedValue;
    }
  }
}