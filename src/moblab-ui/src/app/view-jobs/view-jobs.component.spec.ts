import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBarModule } from '@angular/material';
import { MatSortModule } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { WidgetsModule } from '../widgets/widgets.module';
import {By} from '@angular/platform-browser';

import { Job } from '../services/moblabrpc_pb';
import { ViewJobsComponent } from './view-jobs.component';
import {
  CHECKBOX_ID
} from '../widgets/table-header-selector/table-header-selector.component';

const NUM_NAMES = 2;
const NUM_IDS = 2;
const NUM_PRIORITIES = Object.keys(Job.Priority).length;
const NUM_STATUS = Object.keys(Job.JobStatus).length;

const BASELINE_TIME = Date.now();
// one hour
const TIME_OFFSET = 3600;

function createMockJobs() {
  const mockFilterJobs = [];
  let running_timestamp = BASELINE_TIME;
  for (let i = 0; i < NUM_NAMES; i++) {
    for (let j = 0; j < NUM_IDS; j++) {
      for (let k = 0; k < NUM_PRIORITIES; k++) {
        for (let l = 0; l < NUM_STATUS; l++) {
          running_timestamp += TIME_OFFSET
          const startTimestamp = running_timestamp ;
          running_timestamp += TIME_OFFSET
          const finishedTimestamp = running_timestamp;
          let mockJob = new Job();
          mockJob.setName('Job' + i.toString());
          mockJob.setJobId(j);
          mockJob.setStartTimeSecUtc(startTimestamp);
          mockJob.setCreatedTimeSecUtc(Date.now());
          mockJob.setFinishedTimeSecUtc(finishedTimestamp);
          mockJob.setPriority(k);
          mockJob.setStatus(l);
          mockFilterJobs.push(mockJob);
        }
      }
    }
  }
  return mockFilterJobs;
}

describe('ViewJobsComponent', () => {
  let component: ViewJobsComponent;
  let fixture: ComponentFixture<ViewJobsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
        imports: [
          BrowserAnimationsModule,
          CommonModule,
          FormsModule,
          MatButtonModule,
          MatCardModule,
          MatCheckboxModule,
          MatChipsModule,
          MatExpansionModule,
          MatFormFieldModule,
          MatIconModule,
          MatInputModule,
          MatListModule,
          MatProgressSpinnerModule,
          MatSelectModule,
          MatSnackBarModule,
          MatSortModule,
          MatTableModule,
          ReactiveFormsModule,
          WidgetsModule,
        ],
        declarations: [
          ViewJobsComponent]})
        .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ViewJobsComponent);
    component = fixture.componentInstance;
    // @ts-ignore
    spyOn<any>(component.moblabGrpcService, 'getJobs')
      .and.callFake(function() {
      component.assignJobs(createMockJobs());
    });
    fixture.detectChanges();
  });

  it('Minimal, creation test.', () => {
    expect(component).toBeTruthy();
  });

  it ('Checking that jobs are loaded in.', () => {
    expect(component.getNumJobs()).toBe(createMockJobs().length);
  });

  //////////////////////////////////////////////////// Checkbox tests
  it('Verifying no jobs checked initially.', () => {
    expect(component.getNumSelectedJobs()).toBe(0);
  });

  it ('Checking all jobs then un-checking all jobs.',
    () => {
    const selectJobsButton = fixture.debugElement.nativeElement.querySelector(
      '#' + CHECKBOX_ID
    );
    expect(component.getNumSelectedJobs()).toBe(0);
    selectJobsButton.dispatchEvent(new Event('change'));

    expect(component.getNumSelectedJobs()).toBe(component.getNumJobs());

    selectJobsButton.dispatchEvent(new Event('change'));
    expect(component.getNumSelectedJobs()).toBe(0);
  });

  it ('Checking one job, then checking all jobs.', () => {
    const selectJobsButton = fixture.debugElement.nativeElement.querySelector(
      '#' + CHECKBOX_ID
    );
    component.job_selections.select(component.jobs.data[0]);
    expect(component.getNumSelectedJobs()).toBe(1);
    selectJobsButton.dispatchEvent(new Event('change'));
    expect(component.getNumSelectedJobs()).toBe(component.getNumJobs());
  });

  it ('Checking all jobs, then unchecking one job, then' +
    ' unchecking all jobs, then re-checking all jobs.', () => {
    const selectJobsButton = fixture.debugElement.nativeElement.querySelector(
      '#' + CHECKBOX_ID
    );
    selectJobsButton.dispatchEvent(new Event('change'));
    expect(component.getNumSelectedJobs()).toBe(component.getNumJobs());
    component.job_selections.deselect(component.jobs.data[0]);
    expect(component.getNumSelectedJobs()).toBe(
      component.getNumJobs() - 1
    );
    selectJobsButton.dispatchEvent(new Event('change'));
    expect(component.getNumSelectedJobs()).toBe(0);
    selectJobsButton.dispatchEvent(new Event('change'));
    expect(component.getNumSelectedJobs()).toBe(component.getNumJobs());
  });

  it ('Testing multiple single selections.', () => {
    component.job_selections.select(component.jobs.data[0]);
    expect(component.getNumSelectedJobs()).toBe(1);
    component.job_selections.select(component.jobs.data[1]);
    expect(component.getNumSelectedJobs()).toBe(2);
  });

  //////////////////////////////////////////////////// Refresh tests
  it ('Testing that refresh successfully reloads data.', function(done) {
    // @ts-ignore
    expect(component.moblabGrpcService.getJobs)
      .toHaveBeenCalledTimes(1);
    const refreshButton = fixture.debugElement.nativeElement.querySelector(
      '.job-refresh-button'
    );
    refreshButton.dispatchEvent(new Event('click'));
    // @ts-ignore
    expect(component.moblabGrpcService.getJobs)
      .toHaveBeenCalledTimes(2);
    setTimeout(function() {
      /*
        Because the RPC call to get jobs has been mocked out, we know it will
        'return' in less than .5 sec, the check below is to ensure that jobs
        are not duplicated on refresh calls.
      */
      expect(component.getNumJobs()).toBe(createMockJobs().length);
      done();
    }, 500);
  });

  //////////////////////////////////////////////////// Filter tests

  it('Testing start date lower and upper bound filters.', function () {
    // Setting up lower bound start filter to get rid of half of the jobs.
    const startFromFilterInput =
      fixture.debugElement.nativeElement.querySelector(
      '#startFromTimeInput'
    );
    startFromFilterInput.value = new Date(
      BASELINE_TIME + createMockJobs().length * TIME_OFFSET
    ).toLocaleString();
    startFromFilterInput.dispatchEvent(new Event('input'));
    expect(component.getNumVisibleJobs()).toBe(
      createMockJobs().length / 2
    );

    // Setting up upper bound as well, to let only one job through.
    const startToFilterInput =
      fixture.debugElement.nativeElement.querySelector(
      '#startToTimeInput'
    );
    startToFilterInput.value = new Date(
      BASELINE_TIME + (createMockJobs().length + 2) * TIME_OFFSET
    ).toLocaleString();
    startToFilterInput.dispatchEvent(new Event('input'));

    expect(component.getNumVisibleJobs()).toBe(1);
  });

  it('Test that NaN dates do not have any filtering effect.', function () {
    const startFromFilterInput =
      fixture.debugElement.nativeElement.querySelector(
        '#startFromTimeInput'
      );
    /*
      Setting an input value start date filter that would filter out all jobs,
      except a char is added to make the string malformed.
    */
    startFromFilterInput.value = new Date(
      BASELINE_TIME + createMockJobs().length * TIME_OFFSET * 10
    ).toLocaleString() + 'x';
    startFromFilterInput.dispatchEvent(new Event('input'));

    expect(component.getNumVisibleJobs()).toBe(createMockJobs().length);
  });

  /*
    This test verifies that multiple filters work together correctly. The mock
    jobs are set up to create one of each permutation across name, id, status
    and priority. The idea of this test is that by incrementally setting
    filters for each of these attributes, the number of visible jobs will each
    time be reduced by a factor of n where n is the number of different
    possible value of the attribute ( free text attributes name and id are only
    given two possible values in the mock job creator ).
  */
  it('Verifying that multiple filters work together.', function () {
    let expectedNumJobs = component.getNumJobs();

    const nameFilterInput = fixture.debugElement.nativeElement.querySelector(
      '#nameInput'
    );
    nameFilterInput.value = '0';
    nameFilterInput.dispatchEvent(new Event('input'));

    expectedNumJobs = expectedNumJobs / NUM_NAMES;
    expect(component.getNumVisibleJobs()).toBe(expectedNumJobs);

    const idFilterInput = fixture.debugElement.nativeElement.querySelector(
      '#idInput'
    );
    idFilterInput.value = '0';
    idFilterInput.dispatchEvent(new Event('input'));

    expectedNumJobs = expectedNumJobs / NUM_IDS;
    expect(component.getNumVisibleJobs()).toBe(expectedNumJobs);

    /*
      TO-DO: Figure out how to wire this change via an element event instead of
      a component operation.
      Tried: selectionChange dispatch on mat-select debugElement, didn't work.
      Tried: change event dispatch on mat-select nativeElement, didn't work.
    */
    component.filters.getFormControl('priority').setValue('DEFAULT');

    expectedNumJobs = expectedNumJobs / NUM_PRIORITIES;
    expect(component.getNumVisibleJobs()).toBe(expectedNumJobs);

    /*
      TO-DO: Figure out how to wire this change via an element event instead of
      component operation.
    */
    component.filters.getFormControl('jobStatus').setValue('RUNNING');

    expect(component.getNumVisibleJobs()).toBe(1);
  });

  it('Verifiying that refresh clears filters.', function () {
    // create a filter event that filters out all jobs.
    const nameFilterInput = fixture.debugElement.nativeElement.querySelector(
      '#nameInput'
    );
    nameFilterInput.value = 'This will not match with any jobs';
    nameFilterInput.dispatchEvent(new Event('input'));

    expect(component.getNumVisibleJobs()).toBe(0);

    const refreshButton = fixture.debugElement.nativeElement.querySelector(
      '.job-refresh-button'
    );
    refreshButton.dispatchEvent(new Event('click'));

    // verify that after refresh all jobs are visible again
    expect(component.getNumVisibleJobs()).toBe(component.getNumJobs());
  });
});
