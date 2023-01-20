import {BrowserModule} from '@angular/platform-browser';
import {FormsModule} from '@angular/forms';
import {MatAutocompleteModule} from '@angular/material/autocomplete';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatDividerModule} from '@angular/material/divider';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatRadioModule} from '@angular/material/radio';
import {MatSelectModule} from '@angular/material/select';
import {MatTabsModule} from '@angular/material/tabs';
import {MatTooltipModule} from '@angular/material/tooltip';
import {NgModule} from '@angular/core';
import {ReactiveFormsModule} from '@angular/forms';
import {RouterModule} from '@angular/router';

import {BasicAutocompleteSelectorComponent} from './common/basic-autocomplete-selector/basic-autocomplete-selector.component';
import {BasicCheckboxFormComponent} from './common/basic-checkbox/basic-checkbox.component';
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
import {StorageQualV2Component} from './custom-run-suite/storage-qual-v2/storage-qual-v2.component';
import {StorageQualComponent} from './custom-run-suite/storage-qual/storage-qual.component';
import {WidgetsModule} from './../widgets/widgets.module';
import {NewUpdateNotifierComponent} from './common/new-update-notifier/new-update-notifier.component';
import {NewUpdateModule} from '../directives/new-update/new-update.module';
import {FAFTRunComponent} from './custom-run-suite/faft/faft.component';
import {CUJRunComponent} from './custom-run-suite/cuj/cuj.component';
import {PvsComponent} from './custom-run-suite/pvs/pvs.component';
import {FWUPDRunComponent} from './custom-run-suite/fwupd/fwupd.component';

@NgModule({
  declarations: [
    BasicAutocompleteSelectorComponent,
    BasicCheckboxFormComponent,
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
    StorageQualV2Component,
    NewUpdateNotifierComponent,
    FAFTRunComponent,
    CUJRunComponent,
    PvsComponent,
    FWUPDRunComponent,
  ],
  exports: [
    BasicAutocompleteSelectorComponent,
    BasicSelectorComponent,
    BuildSelectFormsComponent,
    BvtComponent,
    CtsRunComponent,
    MemoryQualComponent,
    PowerComponent,
    RunAnySuiteComponent,
    RunSuiteComponent,
    StorageQualComponent,
    StorageQualV2Component,
    FAFTRunComponent,
    CUJRunComponent,
    FWUPDRunComponent,
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
    MatRadioModule,
    MatSelectModule,
    MatTabsModule,
    MatTooltipModule,
    ReactiveFormsModule,
    RouterModule,
    WidgetsModule,
    NewUpdateModule,
  ],
})
export class RunSuiteModule {}
