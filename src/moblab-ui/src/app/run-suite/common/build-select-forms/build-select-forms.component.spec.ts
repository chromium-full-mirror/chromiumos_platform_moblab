/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatInputModule} from '@angular/material/input';
import {MatTooltipModule} from '@angular/material/tooltip';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatSelectModule} from '@angular/material/select';

import {BasicSelectorComponent} from '../basic-selector/basic-selector.component';
import {BuildSelectFormsComponent} from './build-select-forms.component';

describe('BuildSelectFormsComponent', () => {
  let component: BuildSelectFormsComponent;
  let fixture: ComponentFixture<BuildSelectFormsComponent>;

  let listModelsSpy: jasmine.Spy;
  let listBuildTargetsSpy: jasmine.Spy;
  let listBuildVersionsSpy: jasmine.Spy;
  let listPoolsSpy: jasmine.Spy;
  let allRequiredFieldsEmitter: jasmine.Spy;

  let boardSelectorComponent: BasicSelectorComponent;
  let modelSelectorComponent: BasicSelectorComponent;
  let buildSelectorComponent: BasicSelectorComponent;
  let poolSelectorComponent: BasicSelectorComponent;

  function applySelection(targetComponent: BasicSelectorComponent, value: string) {
    targetComponent.onChange({'value' : value});
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
          MatTooltipModule,
          ReactiveFormsModule,
        ],
        declarations: [
          BasicSelectorComponent,
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
    listBuildTargetsSpy = spyOn<any>(component.moblabGrpcService, 'listBuildTargets').and.callFake(() => {
      component.updateBuildTargets(['BuildTarget1', 'BuildTarget2']);
    });
    // @ts-ignore
    listBuildVersionsSpy = spyOn<any>(component.moblabGrpcService, 'listBuildVersions').and.callFake(() => {
      component.updateBuildTargets(['BuildVersion/1', 'BuildVersion/2']);
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

  it('Check that selections work in order.', () => {
    expect(modelSelectorComponent.isDisabled()).toBe(false);
    expect(boardSelectorComponent.isDisabled()).toBe(true);
    expect(buildSelectorComponent.isDisabled()).toBe(true);
    expect(poolSelectorComponent.isDisabled()).toBe(true);

    applySelection(modelSelectorComponent, 'MockModel1');
    expect(boardSelectorComponent.isDisabled()).toBe(false);

    applySelection(boardSelectorComponent, 'BuildTarget1');
    expect(buildSelectorComponent.isDisabled()).toBe(false);

    applySelection(buildSelectorComponent, 'BuildVersion/1');
    expect(poolSelectorComponent.isDisabled()).toBe(false);
    expect(allRequiredFieldsEmitter).toHaveBeenCalledTimes(1);
  });
});
