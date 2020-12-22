/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {By} from '@angular/platform-browser';
import {DebugElement} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatTableModule} from '@angular/material/table';
import {MatTooltipModule} from '@angular/material/tooltip';
import {RouterModule} from '@angular/router';

import {ConnectedDutInfo, Job} from '../../services/moblabrpc_pb';
import {EditAttributesComponent} from './edit-attributes.component';
import {PipesModule} from 'app/pipes/pipes.module';
import {ViewDutsComponent} from '../view-duts/view-duts.component';
import {WidgetsModule} from 'app/widgets/widgets.module';

function createMockDuts(): ConnectedDutInfo[] {
  const mockDuts = [];
  for (let i = 0; i < 10; i++) {
    const mockDut = new ConnectedDutInfo();
    mockDut.setName('MockDUT' + i.toString());
    mockDuts.push(mockDut);
  }
  return mockDuts;
}

describe('EditAttributesComponent', () => {
  let component: EditAttributesComponent;
  let fixture: ComponentFixture<EditAttributesComponent>;
  let dutsTableSpy: jasmine.Spy;
  let addAttributeToDutsSpy: jasmine.Spy;
  let removeAttributeFromDutsSpy: jasmine.Spy;
  let addLabelToDutsSpy: jasmine.Spy;
  let removeLabelFromDutsSpy: jasmine.Spy;
  let addPoolToDutsSpy: jasmine.Spy;
  let removePoolFromDutsSpy: jasmine.Spy;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        FormsModule,
        MatCardModule,
        MatCheckboxModule,
        MatFormFieldModule,
        MatIconModule,
        MatInputModule,
        MatProgressSpinnerModule,
        MatSnackBarModule,
        MatTableModule,
        MatTooltipModule,
        PipesModule,
        ReactiveFormsModule,
        RouterModule,
        WidgetsModule,
      ],
      declarations: [EditAttributesComponent, ViewDutsComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditAttributesComponent);
    component = fixture.componentInstance;

    // @ts-ignore
    addAttributeToDutsSpy = spyOn<any>(
      component.moblabGrpcService,
      'addAttributeToDuts'
    );
    // @ts-ignore
    removeAttributeFromDutsSpy = spyOn<any>(
      component.moblabGrpcService,
      'removeAttributeFromDuts'
    );
    // @ts-ignore
    addLabelToDutsSpy = spyOn<any>(
      component.moblabGrpcService,
      'addLabelToDuts'
    );
    // @ts-ignore
    removeLabelFromDutsSpy = spyOn<any>(
      component.moblabGrpcService,
      'removeLabelFromDuts'
    );
    // @ts-ignore
    addPoolToDutsSpy = spyOn<any>(component.moblabGrpcService, 'addPoolToDuts');
    // @ts-ignore
    removePoolFromDutsSpy = spyOn<any>(
      component.moblabGrpcService,
      'removePoolFromDuts'
    );
    fixture.detectChanges();
  });

  function inputEditValue(formId: string, val: string) {
    const editInput = fixture.debugElement.nativeElement.querySelector(formId);
    editInput.value = val;
    editInput.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  function dispatchButtonClick(buttonId: string) {
    const button = fixture.debugElement.nativeElement.querySelector(buttonId);
    button.dispatchEvent(new Event('click'));
    fixture.detectChanges();
  }

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('expect that action will not be done with no selected DUTs', () => {
    inputEditValue('#label-input', 'test-label');
    dispatchButtonClick('#add-label-button');

    expect(addLabelToDutsSpy).toHaveBeenCalledTimes(0);
  });

  describe('Submission tests', () => {
    beforeEach(() => {
      dutsTableSpy = spyOn<any>(
        component.dutsTableRef,
        'getSelectedDutHostnames'
      ).and.callFake(createMockDuts);
    });

    it('expect that add label submission gets passed through.', () => {
      inputEditValue('#label-input', 'test-label');
      dispatchButtonClick('#add-label-button');

      expect(addLabelToDutsSpy).toHaveBeenCalled();
    });

    it('expect that remove label submission gets passed through.', () => {
      inputEditValue('#label-input', 'test-label');
      dispatchButtonClick('#remove-label-button');

      expect(removeLabelFromDutsSpy).toHaveBeenCalled();
    });

    it('expect that add attribute submission gets passed through.', () => {
      inputEditValue('#attribute-key-input', 'test-key');
      inputEditValue('#attribute-value-input', 'test-value');
      dispatchButtonClick('#add-attribute-button');

      expect(addAttributeToDutsSpy).toHaveBeenCalled();
    });

    it('expect that remove attribute submission gets passed through.', () => {
      inputEditValue('#attribute-key-input', 'test-key');
      dispatchButtonClick('#remove-attribute-button');

      expect(removeAttributeFromDutsSpy).toHaveBeenCalled();
    });

    it('expect that add pool submission gets passed through.', () => {
      inputEditValue('#pool-input', 'test-pool');
      dispatchButtonClick('#add-pool-button');

      expect(addPoolToDutsSpy).toHaveBeenCalled();
    });

    it('expect that remove pool submission gets passed through.', () => {
      inputEditValue('#pool-input', 'test-pool');
      dispatchButtonClick('#remove-pool-button');

      expect(removePoolFromDutsSpy).toHaveBeenCalled();
    });
  });
});
