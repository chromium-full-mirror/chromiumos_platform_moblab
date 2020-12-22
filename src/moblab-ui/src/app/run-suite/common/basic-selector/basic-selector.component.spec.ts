/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {Component} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatCardModule} from '@angular/material/card';
import {MatInputModule} from '@angular/material/input';
import {MatSelectModule} from '@angular/material/select';
import {MatTooltipModule} from '@angular/material/tooltip';

import {BasicSelectorComponent} from './basic-selector.component';

@Component({
  selector: 'basic-selector-test-wrapper',
  template: `
    <app-basic-selector
      #modelSelector
      [title]="'Select option:'"
      [placeholder]="['Pick from available options']"
      [options]="['MockOption1']"
      [isShown]="true"
      (select)="selectChanged($event.value)"
    >
    </app-basic-selector>
  `,
})
class BasicSelectorTestWrapperComponent {
  selectChanged(event) {}
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
      declarations: [BasicSelectorComponent, BasicSelectorTestWrapperComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    wrapperFixture = TestBed.createComponent(BasicSelectorTestWrapperComponent);
    component = wrapperFixture.debugElement.children[0].componentInstance;
    wrapperFixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('check that one option selector autocompletes.', () => {
    expect(component.getSelectedValue()).toBe('MockOption1');
  });

  it('expect selected Output to fire on selection', () => {
    const select = wrapperFixture.debugElement.nativeElement.querySelector(
      '.mat-select'
    );
    // new MatOptionSelectionChange(new MatOption(1,1,1,1))
    // select.dispatchEvent(new Event('input'));
    // wrapperFixture.debugElement.query(By.css('mat-select')).triggerEventHandler('selectionChange', { value: { id: 1 } });
    spyOn(component.select, 'emit').and.callThrough();

    select.dispatchEvent(new Event('selectionChange'));
    wrapperFixture.detectChanges();
    expect(component.select.emit).toHaveBeenCalledTimes(1);
  });
});
