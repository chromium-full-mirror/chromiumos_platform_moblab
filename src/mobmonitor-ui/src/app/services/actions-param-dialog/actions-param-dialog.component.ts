import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'mob-actions-param-dialog',
  templateUrl: './actions-param-dialog.component.html',
  styleUrls: ['./actions-param-dialog.component.scss']
})
export class ActionsParamDialogComponent implements OnInit {
  // List of parameter definitions that will generate the form
  // each definition has a name and an info
  paramDefinitions = [];

  // model binding for the params, each param will have an entry
  // in the map
  params = {};

  constructor(
    public dialogRef: MatDialogRef<ActionsParamDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  ngOnInit() {
    // initialize the params model and paramDefinitions array
    // using the injected param data
    for (const key of Object.keys(this.data.params)) {
      this.paramDefinitions.push({
        name: key,
        info: this.data.params[key]
      });
      this.params[key] = '';
    }
  }

  onNoClick() {
    // close the dialog with no return value, user
    // didn't finish the form
    this.dialogRef.close();
  }

  runAction() {
    // close the dialog with the 'return value' of the param
    // values entered into the form
    this.dialogRef.close(this.params);
  }
}
