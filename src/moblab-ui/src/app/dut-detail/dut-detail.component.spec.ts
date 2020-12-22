/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatDividerModule} from '@angular/material/divider';
import {MatExpansionModule} from '@angular/material/expansion';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatPaginatorModule} from '@angular/material/paginator';
import {MatTableModule} from '@angular/material/table';
import {ReactiveFormsModule} from '@angular/forms';
import {RouterTestingModule} from '@angular/router/testing';

import {ConnectedDutInfo} from '../services/moblabrpc_pb';
import {DutDetailComponent} from './dut-detail.component';
import {DutTaskTableComponent} from './dut_task_table/dut_task_table.component';
import {ViewJobsModule} from '../view-jobs/view-jobs.module';
import {WidgetsModule} from '../widgets/widgets.module';

function createMockDutDetailInfo(dut: string) {
  const mockDutDetailInfo = new ConnectedDutInfo();
  mockDutDetailInfo.setIp(dut);
  mockDutDetailInfo.setName('Mock DUT');
  mockDutDetailInfo.setLabelsList(['label1', 'label2', 'label3']);
  return mockDutDetailInfo;
}

describe('DutDetailComponent', () => {
  let component: DutDetailComponent;
  let fixture: ComponentFixture<DutDetailComponent>;

  let getDutDetailsSpy: jasmine.Spy;
  let repairDutSpy: jasmine.Spy;
  let reverifyDutSpy: jasmine.Spy;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        CommonModule,
        FormsModule,
        MatButtonModule,
        MatCardModule,
        MatDividerModule,
        MatExpansionModule,
        MatFormFieldModule,
        MatIconModule,
        MatInputModule,
        MatPaginatorModule,
        MatTableModule,
        ReactiveFormsModule,
        RouterTestingModule,
        ViewJobsModule,
        WidgetsModule,
      ],
      declarations: [DutDetailComponent, DutTaskTableComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DutDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  beforeEach(() => {
    // @ts-ignore
    repairDutSpy = spyOn<any>(component.moblabGrpcService, 'repairDut');
    // @ts-ignore
    reverifyDutSpy = spyOn<any>(component.moblabGrpcService, 'reverifyDut');
    // @ts-ignore
    getDutDetailsSpy = spyOn<any>(
      component.moblabGrpcService,
      'getDutTasks'
    ).and.callFake(
      (
        callback: (x: ConnectedDutInfo) => void,
        errorHandlingCallback: (errorMsg: string) => void,
        dut: string
      ) => {
        component.setDutDetails(createMockDutDetailInfo(dut));
      }
    );
    fixture.detectChanges();
  });

  function inputDutQuery(val) {
    const dutQueryInput = fixture.debugElement.nativeElement.querySelector(
      '#dut-query-input'
    );
    dutQueryInput.value = val;
    dutQueryInput.dispatchEvent(new Event('input'));

    const jobQueryButton = fixture.debugElement.nativeElement.querySelector(
      '#dut-query-button'
    );
    jobQueryButton.dispatchEvent(new Event('click'));
    fixture.detectChanges();
  }

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('verify that repair/reverify task buttons disabled prior to DUT load.', () => {
    const repairButton = fixture.debugElement.nativeElement.querySelector(
      '#repair-button'
    );
    const reverifyButton = fixture.debugElement.nativeElement.querySelector(
      '#reverify-button'
    );
    expect(repairButton.disabled).toBeTruthy();
    expect(reverifyButton.disabled).toBeTruthy();
  });

  it('load and refresh of DUT detail information works.', () => {
    expect(getDutDetailsSpy).not.toHaveBeenCalled();
    inputDutQuery('000.000.000.000');
    expect(getDutDetailsSpy).toHaveBeenCalled();

    getDutDetailsSpy.calls.reset();
    expect(getDutDetailsSpy).not.toHaveBeenCalled();

    fixture.debugElement.nativeElement
      .querySelector('#dut-refresh-button')
      .dispatchEvent(new Event('click'));

    expect(getDutDetailsSpy).toHaveBeenCalled();

    // Repair and reverify buttons should be clickable after DUT load.
    const repairButton = fixture.debugElement.nativeElement.querySelector(
      '#repair-button'
    );
    const reverifyButton = fixture.debugElement.nativeElement.querySelector(
      '#reverify-button'
    );
    expect(repairButton.disabled).toBeFalsy();
    expect(reverifyButton.disabled).toBeFalsy();
  });

  it('repair and reverify submissions fire.', () => {
    inputDutQuery('000.000.000.000');

    fixture.debugElement.nativeElement
      .querySelector('#reverify-button')
      .dispatchEvent(new Event('click'));
    expect(reverifyDutSpy).toHaveBeenCalled();

    fixture.debugElement.nativeElement
      .querySelector('#repair-button')
      .dispatchEvent(new Event('click'));
    expect(repairDutSpy).toHaveBeenCalled();
  });
});
