import {CommonModule} from '@angular/common';
import {NgModule} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {MatButtonModule, MatCheckboxModule, MatOptionModule, MatTabGroup, MatTableModule, MatTabsModule} from '@angular/material';
import {MatCardModule} from '@angular/material/card';
import {MatSelectModule} from '@angular/material/select';
import {BrowserModule} from '@angular/platform-browser';
import {RouterModule} from '@angular/router';
import {PipesModule} from 'app/pipes/pipes.module';
import {WidgetsModule} from 'app/widgets/widgets.module';

import {ServicesModule} from '../services/services.module';

import {EnrollmentComponent} from './enrollment/enrollment.component';
import {FirmwareComponent} from './firmware/firmware.component';
import {ManageDutsComponent} from './manage-duts.component';


@NgModule({
  imports: [
    MatCheckboxModule, MatTabsModule, FormsModule, MatCardModule,
    MatButtonModule, MatTableModule, MatOptionModule, MatSelectModule,
    PipesModule, ServicesModule
  ],
  declarations: [ManageDutsComponent, EnrollmentComponent, FirmwareComponent],
  exports: [
    ManageDutsComponent,
  ]
})
export class ManageDutsModule {
}
