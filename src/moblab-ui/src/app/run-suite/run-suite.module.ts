import {BrowserModule} from '@angular/platform-browser';
import {FormsModule} from '@angular/forms';
import {MatAutocompleteModule} from '@angular/material/autocomplete';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatDividerModule} from '@angular/material/divider';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatSelectModule} from '@angular/material/select';
import {MatTabsModule} from '@angular/material/tabs';
import {MatTooltipModule} from '@angular/material/tooltip';
import {NgModule} from '@angular/core';
import {ReactiveFormsModule} from '@angular/forms';
import {RouterModule} from '@angular/router';

import {BasicAutocompleteSelectorComponent} from './common/basic-autocomplete-selector/basic-autocomplete-selector.component';
import {BasicInputFormComponent} from './common/basic-input-form/basic-input.component';
import {BasicSelectorComponent} from './common/basic-selector/basic-selector.component';
import {BasicTextFormComponent} from './common/basic-text-form/basic-text-form.component';
import {BuildSelectFormsComponent} from './common/build-select-forms/build-select-forms.component';
import {BvtComponent} from './custom-run-suite/bvt/bvt.component';
import {CtsRunComponent} from './custom-run-suite/cts-run/cts-run.component';
import {GtsRunComponent} from './custom-run-suite/gts-run/gts-run.component';
import {MemoryQualComponent} from './custom-run-suite/memory-qual/memory-qual.component';
import {PowerComponent} from './custom-run-suite/power/power.component';
import {RunAnySuiteComponent} from './run-any-suite/run-any-suite.component';
import {RunSuiteButtonComponent} from './common/run-suite-button/run-suite-button.component';
import {RunSuiteComponent} from './run-suite.component';
import {StorageQualComponent} from './custom-run-suite/storage-qual/storage-qual.component';
import {WidgetsModule} from './../widgets/widgets.module';

@NgModule({
  declarations: [
    BasicAutocompleteSelectorComponent,
    BasicInputFormComponent,
    BasicSelectorComponent,
    BasicTextFormComponent,
    BuildSelectFormsComponent,
    BvtComponent,
    CtsRunComponent,
    GtsRunComponent,
    MemoryQualComponent,
    PowerComponent,
    RunAnySuiteComponent,
    RunSuiteButtonComponent,
    RunSuiteComponent,
    StorageQualComponent,
  ],
  exports: [
    BvtComponent,
    CtsRunComponent,
    MemoryQualComponent,
    PowerComponent,
    RunAnySuiteComponent,
    RunSuiteComponent,
    StorageQualComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    MatAutocompleteModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatDividerModule,
    MatIconModule,
    MatInputModule,
    MatSelectModule,
    MatTabsModule,
    MatTooltipModule,
    ReactiveFormsModule,
    RouterModule,
    WidgetsModule,
    WidgetsModule,
  ]
})
export class RunSuiteModule {}
