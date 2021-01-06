import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {By} from '@angular/platform-browser';
import {CommonModule} from '@angular/common';
import {Component} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatChipsModule} from '@angular/material/chips';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatListModule} from '@angular/material/list';
import {MatPaginatorModule} from '@angular/material/paginator';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatSelectModule} from '@angular/material/select';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatSortModule} from '@angular/material/sort';
import {MatTableModule} from '@angular/material/table';

import {CHECKBOX_ID} from '../widgets/table-header-selector/table-header-selector.component';
import {JobActionComponent} from './job-action/job-action.component';
import {Job} from '../services/moblabrpc_pb';
import {RouterModule} from '@angular/router';
import {ViewJobsComponent} from './view-jobs.component';
import {WidgetsModule} from '../widgets/widgets.module';

const NUM_NAMES = 2;
const NUM_IDS = 2;
const NUM_PRIORITIES = Object.keys(Job.Priority).length;
const NUM_STATUS = Object.keys(Job.JobStatus).length;

const BASELINE_TIME_SEC = Math.floor(Date.now() / 1000);
// one hour
const TIME_OFFSET_SEC = 3600;

// Creates unique, mock jobs, each a different permutation. Useful for tests on
// filtering.
function createMockJobs(
  id_filter?: string,
  name_filter?: string,
  created_time_lt?: number,
  created_time_gt?: number
) {
  const mockFilterJobs = [];
  let running_timestamp = BASELINE_TIME_SEC;
  for (let i = 0; i < NUM_NAMES; i++) {
    for (let j = 0; j < NUM_IDS; j++) {
      for (let k = 0; k < NUM_PRIORITIES; k++) {
        for (let l = 0; l < NUM_STATUS; l++) {
          running_timestamp += TIME_OFFSET_SEC;
          const startTimestamp = running_timestamp;
          running_timestamp += TIME_OFFSET_SEC;
          const finishedTimestamp = running_timestamp;
          const mockJob = new Job();
          mockJob.setName('Job' + i.toString());
          mockJob.setJobId(mockFilterJobs.length);
          mockJob.setStartTimeSecUtc(startTimestamp);
          mockJob.setCreatedTimeSecUtc(startTimestamp);
          mockJob.setFinishedTimeSecUtc(finishedTimestamp);
          mockJob.setPriority(k * 10);
          mockJob.setStatus(l);
          if (id_filter && !mockJob.getJobId().toString().includes(id_filter)) {
            continue;
          }
          if (name_filter && !mockJob.getName().includes(name_filter)) {
            continue;
          }
          if (
            created_time_lt &&
            created_time_lt <= mockJob.getCreatedTimeSecUtc()
          ) {
            continue;
          }
          if (
            created_time_gt &&
            created_time_gt >= mockJob.getCreatedTimeSecUtc()
          ) {
            continue;
          }
          mockFilterJobs.push(mockJob);
        }
      }
    }
  }
  return mockFilterJobs;
}

function createMockJobIds(
  id_filter?: string,
  name_filter?: string,
  created_time_lt?: number,
  created_time_gt?: number
) {
  const jobs = createMockJobs(
    id_filter,
    name_filter,
    created_time_lt,
    created_time_gt
  );
  const jobIds = [];
  jobs.forEach(job => {
    jobIds.push(job.getJobId());
  });
  return jobIds;
}

@Component({
  selector: 'view-jobs-test-wrapper',
  template: `<app-view-jobs
    [manualPopulate]="true"
    [hideFilters]="true"
    [hideActionBar]="true"
  ></app-view-jobs>`,
})
class ViewJobsTestWrapperComponent { }

describe('ViewJobsComponent', () => {
  let component: ViewJobsComponent;
  let fixture: ComponentFixture<ViewJobsComponent>;

  let getJobIdsSpy: jasmine.Spy;
  let getJobsSpy: jasmine.Spy;
  let getNumJobsSpy: jasmine.Spy;

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
        MatFormFieldModule,
        MatIconModule,
        MatInputModule,
        MatListModule,
        MatProgressSpinnerModule,
        MatPaginatorModule,
        MatSelectModule,
        MatSnackBarModule,
        MatSortModule,
        MatTableModule,
        ReactiveFormsModule,
        RouterModule,
        RouterModule.forRoot([]),
        WidgetsModule,
      ],
      declarations: [
        JobActionComponent,
        ViewJobsComponent,
        ViewJobsTestWrapperComponent,
      ],
    }).compileComponents();
  });

  describe('tests of @Input argument functionality', () => {
    let wrapperFixture: ComponentFixture<ViewJobsTestWrapperComponent>;

    beforeEach(() => {
      fixture = TestBed.createComponent(ViewJobsComponent);
      wrapperFixture = TestBed.createComponent(ViewJobsTestWrapperComponent);
      component = fixture.componentInstance;

      fixture.detectChanges();
      wrapperFixture.detectChanges();
    });

    // The ViewJobsTestWrapperComponent used in this test group is templated to
    // have the manualPopulate flag set to true on initialization.
    it('jobs are not auto-loaded when manual populate flag is set', () => {
      expect(component.getNumVisibleJobs()).toBe(0);
    });

    it('hide filters and hide selectors flags work', () => {
      expect(
        wrapperFixture.debugElement.query(By.css('.filter-box'))
      ).toBeNull();
      expect(
        wrapperFixture.debugElement.query(By.css('.job_checkboxes'))
      ).toBeNull();
    });
  });

  describe('basic/filtering/checkbox tests', function () {
    beforeEach(() => {
      fixture = TestBed.createComponent(ViewJobsComponent);
      component = fixture.componentInstance;
      component.hideActionBar = false;

      // @ts-ignore
      getJobsSpy = spyOn<any>(
        component.moblabGrpcService,
        'getJobs'
      ).and.callFake(
        (
          callback: (x: Job[]) => void,
          errorHandlingCallback: (errorMsg: string) => void,
          queryStart: number,
          queryLimit: number,
          id_filter?: string,
          name_filter?: string,
          created_time_lt?: number,
          created_time_gt?: number,
          status_filter?: Job.QueueStatus,
          rel_filter?: Job.Relationship,
          parent_id_filter?: string,
          dut_hostname_filter?: string
        ) => {
          component.assignJobs(
            createMockJobs(
              id_filter,
              name_filter,
              created_time_lt,
              created_time_gt
            )
          );
        }
      );

      // @ts-ignore
      getJobIdsSpy = spyOn<any>(
        component.moblabGrpcService,
        'getJobIds'
      ).and.callFake(
        (
          callback: (x: Job[]) => void,
          errorHandlingCallback: (errorMsg: string) => void,
          queryStart: number,
          queryLimit: number,
          id_filter?: string,
          name_filter?: string,
          created_time_lt?: number,
          created_time_gt?: number,
          status_filter?: Job.QueueStatus,
          rel_filter?: Job.Relationship,
          parent_id_filter?: string,
          dut_hostname_filter?: string
        ) => {
          component.selectJobIds(
            createMockJobIds(
              id_filter,
              name_filter,
              created_time_lt,
              created_time_gt
            )
          );
        }
      );

      // @ts-ignore
      getNumJobsSpy = spyOn<any>(
        component.moblabGrpcService,
        'getNumJobs'
      ).and.callFake(() => {
        component.numJobs = createMockJobs().length;
      });
      fixture.detectChanges();
    });

    it('minimal, creation test', () => {
      const childDebugElement = fixture.debugElement.query(
        By.directive(JobActionComponent)
      );
      expect(component).toBeTruthy();
    });

    it('jobs are loaded in', () => {
      expect(component.getNumVisibleJobs()).toBe(createMockJobs().length);
    });

    /* Checkbox tests */
    it('no jobs checked initially', () => {
      expect(component.getNumSelectedJobs()).toBe(0);
    });

    function toggleJobSelection(jobId) {
      const jobCheckbox = fixture.debugElement.nativeElement.querySelector(
        '#job_' + jobId.toString()
      );
      jobCheckbox.dispatchEvent(new Event('change'));
    }

    it('all jobs then un-checking all jobs', () => {
      const selectJobsButton = fixture.debugElement.nativeElement.querySelector(
        '#' + CHECKBOX_ID
      );
      expect(component.getNumSelectedJobs()).toBe(0);
      selectJobsButton.dispatchEvent(new Event('change'));

      expect(component.getNumSelectedJobs()).toBe(
        component.getNumVisibleJobs()
      );

      selectJobsButton.dispatchEvent(new Event('change'));
      expect(component.getNumSelectedJobs()).toBe(0);
    });

    it('checking one job, then checking all jobs', () => {
      const selectJobsButton = fixture.debugElement.nativeElement.querySelector(
        '#' + CHECKBOX_ID
      );
      toggleJobSelection(0);
      expect(component.getNumSelectedJobs()).toBe(1);
      selectJobsButton.dispatchEvent(new Event('change'));
      expect(component.getNumSelectedJobs()).toBe(
        component.getNumVisibleJobs()
      );
    });

    it(
      'checking all jobs, then unchecking one job, then' +
      ' unchecking all jobs, then re-checking all jobs',
      () => {
        const selectJobsButton = fixture.debugElement.nativeElement.querySelector(
          '#' + CHECKBOX_ID
        );
        selectJobsButton.dispatchEvent(new Event('change'));
        expect(component.getNumSelectedJobs()).toBe(
          component.getNumVisibleJobs()
        );
        toggleJobSelection(0);
        expect(component.getNumSelectedJobs()).toBe(
          component.getNumVisibleJobs() - 1
        );
        selectJobsButton.dispatchEvent(new Event('change'));
        expect(component.getNumSelectedJobs()).toBe(0);
        selectJobsButton.dispatchEvent(new Event('change'));
        expect(component.getNumSelectedJobs()).toBe(
          component.getNumVisibleJobs()
        );
      }
    );

    it('multiple single selections', () => {
      toggleJobSelection(0);
      expect(component.getNumSelectedJobs()).toBe(1);
      toggleJobSelection(1);
      expect(component.getNumSelectedJobs()).toBe(2);
    });

    /* Refresh tests */
    it('refresh successfully reloads data', done => {
      // @ts-ignore
      expect(component.moblabGrpcService.getJobs).toHaveBeenCalledTimes(1);
      const refreshButton = fixture.debugElement.nativeElement.querySelector(
        '.job-refresh-button'
      );
      refreshButton.dispatchEvent(new Event('click'));
      // @ts-ignore
      expect(component.moblabGrpcService.getJobs).toHaveBeenCalledTimes(2);
      setTimeout(() => {
        /*
          Because the RPC call to get jobs has been mocked out, we know it will
          'return' in less than .5 sec, the check below is to ensure that jobs
          are not duplicated on refresh calls.
        */
        expect(component.getNumVisibleJobs()).toBe(createMockJobs().length);
        done();
      }, 500);
    });

    /* Filter tests */

    it('start date lower and upper bound filters work', () => {
      // Setting up lower bound start filter to get rid of half of the jobs.
      const startFromFilterInput = fixture.debugElement.nativeElement.querySelector(
        '#startFromTimeInput'
      );
      startFromFilterInput.value = new Date(
        // TS timestamps need to be milisecond granularity, hence * 1000.
        (BASELINE_TIME_SEC + createMockJobs().length * TIME_OFFSET_SEC) * 1000
      ).toLocaleString();
      startFromFilterInput.dispatchEvent(new Event('input'));
      const filterButton = fixture.debugElement.nativeElement.querySelector(
        '#filter-button'
      );
      filterButton.dispatchEvent(new Event('click'));
      expect(component.getNumVisibleJobs()).toBe(createMockJobs().length / 2);

      // Setting up upper bound as well, to let only one job through.
      const startToFilterInput = fixture.debugElement.nativeElement.querySelector(
        '#startToTimeInput'
      );
      startToFilterInput.value = new Date(
        // TS timestamps need to be milisecond granularity, hence * 1000.
        (BASELINE_TIME_SEC + (createMockJobs().length + 2) * TIME_OFFSET_SEC) *
        1000
      ).toLocaleString();
      startToFilterInput.dispatchEvent(new Event('input'));
      filterButton.dispatchEvent(new Event('click'));

      expect(component.getNumVisibleJobs()).toBe(1);
    });

    it('NaN dates do not have any filtering effect', () => {
      const startFromFilterInput = fixture.debugElement.nativeElement.querySelector(
        '#startFromTimeInput'
      );
      /*
        Setting an input value start date filter that would filter out all jobs,
        except a char is added to make the string malformed.
      */
      startFromFilterInput.value =
        new Date(
          BASELINE_TIME_SEC + createMockJobs().length * TIME_OFFSET_SEC * 10
        ).toLocaleString() + 'x';
      startFromFilterInput.dispatchEvent(new Event('input'));

      expect(component.getNumVisibleJobs()).toBe(createMockJobs().length);
    });

    function setInputForm(formId, inputValue) {
      const inputForm = fixture.debugElement.nativeElement.querySelector(
        formId
      );
      inputForm.value = inputValue;
      inputForm.dispatchEvent(new Event('input'));
      fixture.detectChanges();
    }

    it('invalid inputs disable filter submission', () => {
      const filterButton = fixture.debugElement.nativeElement.querySelector(
        '#filter-button'
      );
      const startToFilterInput = fixture.debugElement.nativeElement.querySelector(
        '#startToTimeInput'
      );
      const idInput = fixture.debugElement.nativeElement.querySelector(
        '#idInput'
      );

      expect(filterButton.disabled).toBeFalsy();

      // Number that translates to less than 0 timestamp.
      setInputForm('#startToTimeInput', '1000');
      expect(filterButton.disabled).toBeTruthy();

      setInputForm('#startToTimeInput', '');
      expect(filterButton.disabled).toBeFalsy();

      // String that cannot be parsed as a date.
      setInputForm('#startToTimeInput', 'xxxx');
      expect(filterButton.disabled).toBeTruthy();

      setInputForm('#startToTimeInput', '');
      expect(filterButton.disabled).toBeFalsy();

      // ID input that is not a number.
      setInputForm('#idInput', 'x');
      expect(filterButton.disabled).toBeTruthy();
    });

    it('refresh preserves filters', () => {
      const initialNumVisibleJobs = component.getNumVisibleJobs();
      // create a filter event that filters out all jobs.
      expect(component.getNumVisibleJobs()).toBe(initialNumVisibleJobs);

      const refreshButton = fixture.debugElement.nativeElement.querySelector(
        '.job-refresh-button'
      );
      refreshButton.dispatchEvent(new Event('click'));
      expect(component.getNumVisibleJobs()).toBe(initialNumVisibleJobs);

      const nameFilterInput = fixture.debugElement.nativeElement.querySelector(
        '#nameInput'
      );
      nameFilterInput.value = 'This will not match with any jobs';
      nameFilterInput.dispatchEvent(new Event('input'));
      const filterButton = fixture.debugElement.nativeElement.querySelector(
        '#filter-button'
      );
      filterButton.dispatchEvent(new Event('click'));
      expect(component.getNumVisibleJobs()).toBe(0);

      refreshButton.dispatchEvent(new Event('click'));
      expect(component.getNumVisibleJobs()).toBe(0);
    });

    it('clear button clears filters', () => {
      const initialNumVisibleJobs = component.getNumVisibleJobs();

      expect(component.getNumVisibleJobs()).toBe(initialNumVisibleJobs);

      const nameFilterInput = fixture.debugElement.nativeElement.querySelector(
        '#nameInput'
      );
      nameFilterInput.value = 'This will not match with any jobs';
      nameFilterInput.dispatchEvent(new Event('input'));
      const filterButton = fixture.debugElement.nativeElement.querySelector(
        '#filter-button'
      );
      filterButton.dispatchEvent(new Event('click'));

      expect(component.getNumVisibleJobs()).toBe(0);

      const clearButton = fixture.debugElement.nativeElement.querySelector(
        '#clear-filters-button'
      );
      clearButton.dispatchEvent(new Event('click'));
      component.refreshJobs();
      // verify that after clear all jobs are visible again
      expect(component.getNumVisibleJobs()).toBe(initialNumVisibleJobs);
    });
  });

  describe('pagination tests', () => {
    const MOCK_NUM_JOBS = 100;

    // Pagination tests need getJobs RPC calls to be mocked differently than
    // other unit tests.
    function getRandomJobs(
      queryStart,
      queryLimit,
      id_filter?: string,
      name_filter?: string,
      created_time_lt?: number,
      created_time_gt?: number
    ) {
      const jobs = [];
      let lastTimestamp = Date.now();
      // 50 hours
      const timeOffset = 172800;
      const numJobsToCreate = Math.min(queryLimit, MOCK_NUM_JOBS - queryStart);
      for (let i = 0; i < numJobsToCreate; i++) {
        const mockJob = new Job();
        mockJob.setJobId(i);
        mockJob.setName('Job' + i.toString());
        mockJob.setPriority(Math.floor(Math.random() * 100) % 4);
        lastTimestamp = lastTimestamp + Math.floor(timeOffset * Math.random());
        const startTimestamp =
          lastTimestamp + (timeOffset * Math.random()) / 20;
        const finishedTimestamp =
          startTimestamp + (timeOffset * Math.random()) / 5;
        mockJob.setCreatedTimeSecUtc(lastTimestamp);
        mockJob.setStartTimeSecUtc(startTimestamp);
        mockJob.setFinishedTimeSecUtc(finishedTimestamp);
        mockJob.setStatus(Math.floor(Math.random() * 100) % 7);

        if (id_filter && !mockJob.getJobId().toString().includes(id_filter)) {
          continue;
        }
        if (name_filter && !mockJob.getName().includes(name_filter)) {
          continue;
        }
        if (
          created_time_lt &&
          created_time_lt >= mockJob.getCreatedTimeSecUtc()
        ) {
          continue;
        }
        if (
          created_time_gt &&
          created_time_gt <= mockJob.getCreatedTimeSecUtc()
        ) {
          continue;
        }
        jobs.push(mockJob);
      }
      return jobs;
    }

    beforeEach(() => {
      fixture = TestBed.createComponent(ViewJobsComponent);
      component = fixture.componentInstance;
      // @ts-ignore
      getJobsSpy = spyOn<any>(
        component.moblabGrpcService,
        'getJobs'
      ).and.callFake(
        (
          callback: (x: Job[]) => void,
          errorHandlingCallback: (errorMsg: string) => void,
          queryStart: number,
          queryLimit: number,
          id_filter?: string,
          name_filter?: string,
          created_time_lt?: number,
          created_time_gt?: number,
          status_filter?: Job.QueueStatus,
          rel_filter?: Job.Relationship,
          parent_id_filter?: string,
          dut_hostname_filter?: string
        ) => {
          const mockJobs = getRandomJobs(
            queryStart,
            queryLimit,
            id_filter,
            name_filter,
            created_time_lt,
            created_time_gt
          );
          component.assignJobs(mockJobs);
        }
      );

      // @ts-ignore
      getNumJobsSpy = spyOn<any>(
        component.moblabGrpcService,
        'getNumJobs'
      ).and.callFake(() => {
        component.numJobs = MOCK_NUM_JOBS;
      });
      fixture.detectChanges();
    });

    it('pagination from start to end to start of jobs list', () => {
      const pageNextButton = fixture.debugElement.nativeElement.querySelector(
        '.mat-paginator-navigation-next'
      );
      const pagePrevButton = fixture.debugElement.nativeElement.querySelector(
        '.mat-paginator-navigation-previous'
      );

      expect(pageNextButton.disabled).toBe(false);
      expect(pagePrevButton.disabled).toBe(true);

      // Going forwards in pages.
      for (
        let i = 0;
        i < MOCK_NUM_JOBS / component.paginator.pageSize - 2;
        i++
      ) {
        pageNextButton.dispatchEvent(new Event('click'));
        expect(component.getNumVisibleJobs()).toBe(
          component.paginator.pageSize
        );
        fixture.detectChanges();
        expect(pageNextButton.disabled).toBe(false);
        expect(pagePrevButton.disabled).toBe(false);
      }

      pageNextButton.dispatchEvent(new Event('click'));
      fixture.detectChanges();
      // At this point, the end of the job list should have been reached.
      expect(pageNextButton.disabled).toBe(true);
      expect(pagePrevButton.disabled).toBe(false);

      // Going backwards in pages.
      for (
        let i = 0;
        i < MOCK_NUM_JOBS / component.paginator.pageSize - 2;
        i++
      ) {
        pagePrevButton.dispatchEvent(new Event('click'));
        expect(component.getNumVisibleJobs()).toBe(
          component.paginator.pageSize
        );
        fixture.detectChanges();
        expect(pageNextButton.disabled).toBe(false);
        expect(pagePrevButton.disabled).toBe(false);
      }

      pagePrevButton.dispatchEvent(new Event('click'));
      fixture.detectChanges();
      // At this point, the start of the job list should have been reached again.
      expect(pageNextButton.disabled).toBe(false);
      expect(pagePrevButton.disabled).toBe(true);
    });
  });
});
