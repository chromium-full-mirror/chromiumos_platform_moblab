/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {Component, DebugElement} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatCardModule} from '@angular/material/card';
import {MatInputModule} from '@angular/material/input';
import {MatSelectModule} from '@angular/material/select';
import {MatTooltipModule} from '@angular/material/tooltip';

import {BasicSelectorComponent} from './basic-selector.component';


@Component({
  selector: 'basic-selector-test-wrapper',
  template:
    `
    <app-basic-selector
        #modelSelector
        [title]="'Select option:'"
        [placeholder]="['Pick from available options']"
        [options]="['MockOption1']"
        [isShown]="true"
        (update)="selectChanged($event.value)">
    </app-basic-selector>
  `,
})
class BasicSelectorTestWrapperComponent {
  selectChanged(event) {
  }
}


describe('BasicSelectorComponent', () => {
  let component: BasicSelectorComponent;
  let wrapperFixture: ComponentFixture<BasicSelectorTestWrapperComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
        imports: [
          FormsModule,
          MatCardModule,
          MatInputModule,
          MatSelectModule,
          MatTooltipModule,
          ReactiveFormsModule,
        ],
        declarations: [
          BasicSelectorComponent,
          BasicSelectorTestWrapperComponent,
        ]})
      .compileComponents();
  }));

  beforeEach(() => {
    wrapperFixture = TestBed.createComponent(BasicSelectorTestWrapperComponent);
    component = wrapperFixture.debugElement.children[0].componentInstance;
    wrapperFixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('Check that one option selector autocompletes.', () => {
    expect(component.getSelectedValue()).toBe('MockOption1');
  });
});
