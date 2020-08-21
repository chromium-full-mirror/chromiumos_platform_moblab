/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatAutocompleteSelectedEvent} from '@angular/material/autocomplete';
import {MatInputModule} from '@angular/material/input';
import {MatOption} from '@angular/material/core';
import {MatTooltipModule} from '@angular/material/tooltip';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatSelectModule} from '@angular/material/select';
import {MatSnackBarModule} from '@angular/material/snack-bar';

import {BasicAutocompleteSelectorComponent} from '../basic-autocomplete-selector/basic-autocomplete-selector.component';
import {BuildSelectFormsComponent} from './build-select-forms.component';

describe('BuildSelectFormsComponent', () => {
  let component: BuildSelectFormsComponent;
  let fixture: ComponentFixture<BuildSelectFormsComponent>;

  let listMilestonesSpy: jasmine.Spy;
  let listModelsSpy: jasmine.Spy;
  let listBuildTargetsSpy: jasmine.Spy;
  let listBuildVersionsSpy: jasmine.Spy;
  let listPoolsSpy: jasmine.Spy;
  let allRequiredFieldsEmitter: jasmine.Spy;

  let boardSelectorComponent: BasicAutocompleteSelectorComponent;
  let modelSelectorComponent: BasicAutocompleteSelectorComponent;
  let milestoneSelectorComponent: BasicAutocompleteSelectorComponent;
  let buildSelectorComponent: BasicAutocompleteSelectorComponent;
  let poolSelectorComponent: BasicAutocompleteSelectorComponent;

  function applySelection(targetComponent: BasicAutocompleteSelectorComponent, value: string) {
    targetComponent.onOptionSelect(new MatAutocompleteSelectedEvent(
      this,
      new MatOption(fixture.nativeElement, null, null, null)
    ));
  }

  beforeEach(async(() => {
    TestBed.configureTestingModule({
        imports: [
          BrowserAnimationsModule,
          FormsModule,
          MatFormFieldModule,
          MatIconModule,
          MatInputModule,
          MatSelectModule,
          MatSnackBarModule,
          MatTooltipModule,
          ReactiveFormsModule,
        ],
        declarations: [
          BasicAutocompleteSelectorComponent,
          BuildSelectFormsComponent,
        ]})
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BuildSelectFormsComponent);
    component = fixture.componentInstance;

    // @ts-ignore
    listModelsSpy = spyOn<any>(component.moblabGrpcService, 'listModels').and.callFake(() => {
      component.updateModels(['Model1', 'Model2']);
    });
    // @ts-ignore
    listMilestonesSpy = spyOn<any>(component.moblabGrpcService, 'listMilestones').and.callFake(() => {
      component.updateMilestones(['R01', 'R02']);
    });
    // @ts-ignore
    listBuildTargetsSpy = spyOn<any>(component.moblabGrpcService, 'listBuildTargets').and.callFake(() => {
      component.updateBuildTargets(['BuildTarget1', 'BuildTarget2']);
    });
    // @ts-ignore
    listBuildVersionsSpy = spyOn<any>(component.moblabGrpcService, 'listBuildVersions').and.callFake(() => {
      component.updateBuildVersions(['BuildVersion/1', 'BuildVersion/2']);
    });
    // @ts-ignore
    listPoolsSpy = spyOn<any>(component.moblabGrpcService, 'listPools').and.callFake(() => {
      component.updatePools(['TestPool1', 'TestPool2']);
    });
    // @ts-ignore
    allRequiredFieldsEmitter = spyOn<any>(component, 'emitBuildSelections');

    fixture.detectChanges();

    modelSelectorComponent = fixture.debugElement.query(By.css(
      '#modelSelector')).componentInstance;
    milestoneSelectorComponent = fixture.debugElement.query(By.css(
      '#milestoneSelector')).componentInstance;
    boardSelectorComponent = fixture.debugElement.query(By.css(
      '#boardSelector')).componentInstance;
    buildSelectorComponent = fixture.debugElement.query(By.css(
      '#buildSelector')).componentInstance;
    poolSelectorComponent = fixture.debugElement.query(By.css(
      '#poolSelector')).componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('selections work in order', () => {
    expect(modelSelectorComponent.isDisabled()).toBe(false);
    expect(boardSelectorComponent.isDisabled()).toBe(true);
    expect(milestoneSelectorComponent.isDisabled()).toBe(true);
    expect(buildSelectorComponent.isDisabled()).toBe(true);
    expect(poolSelectorComponent.isDisabled()).toBe(true);

    applySelection(modelSelectorComponent, 'MockModel1');
    expect(boardSelectorComponent.isDisabled()).toBe(false);

    applySelection(boardSelectorComponent, 'BuildTarget1');
    expect(milestoneSelectorComponent.isDisabled()).toBe(false);

    applySelection(milestoneSelectorComponent, 'R01');
    expect(buildSelectorComponent.isDisabled()).toBe(false);

    applySelection(buildSelectorComponent, 'BuildVersion/1');
    expect(poolSelectorComponent.isDisabled()).toBe(false);
    expect(allRequiredFieldsEmitter).toHaveBeenCalledTimes(1);
  });

  it('updating pool will re-emit build values', () => {
    applySelection(modelSelectorComponent, 'MockModel1');
    applySelection(milestoneSelectorComponent, 'R01');
    applySelection(boardSelectorComponent, 'BuildTarget1');
    applySelection(buildSelectorComponent, 'BuildVersion/1');
    applySelection(poolSelectorComponent, 'TestPool1');
    expect(allRequiredFieldsEmitter).toHaveBeenCalledTimes(2);
  });
});
