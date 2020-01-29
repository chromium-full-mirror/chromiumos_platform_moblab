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
import { MatPaginatorModule } from '@angular/material/paginator';
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

// Creates unique, mock jobs, each a different permutation. Useful for tests on
// filtering.
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
          mockJob.setPriority(k*10);
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
          MatExpansionModule,
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
          WidgetsModule,
        ],
        declarations: [
          ViewJobsComponent]})
        .compileComponents();
  });

  describe('Basic/Filtering/Checkbox tests.', function () {
    beforeEach(() => {
      fixture = TestBed.createComponent(ViewJobsComponent);
      component = fixture.componentInstance;
      // @ts-ignore
      getJobsSpy = spyOn<any>(component.moblabGrpcService, 'getJobs')
        .and.callFake(function() {
        component.assignJobs(createMockJobs());
      });
      // @ts-ignore
      getNumJobsSpy = spyOn<any>(component.moblabGrpcService, 'getNumJobs')
        .and.callFake(function() {
          component.numJobs = createMockJobs().length;
        });
      fixture.detectChanges();
    });

    it('Minimal, creation test.', () => {
      expect(component).toBeTruthy();
    });

    it ('Checking that jobs are loaded in.', () => {
      expect(component.getNumVisibleJobs()).toBe(createMockJobs().length);
    });

    /* Checkbox tests */
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

      expect(component.getNumSelectedJobs()).toBe(component.getNumVisibleJobs());

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
      expect(component.getNumSelectedJobs()).toBe(component.getNumVisibleJobs());
    });

    it ('Checking all jobs, then unchecking one job, then' +
      ' unchecking all jobs, then re-checking all jobs.', () => {
      const selectJobsButton = fixture.debugElement.nativeElement.querySelector(
        '#' + CHECKBOX_ID
      );
      selectJobsButton.dispatchEvent(new Event('change'));
      expect(component.getNumSelectedJobs()).toBe(component.getNumVisibleJobs());
      component.job_selections.deselect(component.jobs.data[0]);
      expect(component.getNumSelectedJobs()).toBe(
        component.getNumVisibleJobs() - 1
      );
      selectJobsButton.dispatchEvent(new Event('change'));
      expect(component.getNumSelectedJobs()).toBe(0);
      selectJobsButton.dispatchEvent(new Event('change'));
      expect(component.getNumSelectedJobs()).toBe(component.getNumVisibleJobs());
    });

    it ('Testing multiple single selections.', () => {
      component.job_selections.select(component.jobs.data[0]);
      expect(component.getNumSelectedJobs()).toBe(1);
      component.job_selections.select(component.jobs.data[1]);
      expect(component.getNumSelectedJobs()).toBe(2);
    });

    /* Refresh tests */
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
        expect(component.getNumVisibleJobs()).toBe(createMockJobs().length);
        done();
      }, 500);
    });

    /* Filter tests */

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

    it('Verifiying that refresh clears filters.', function () {
      const initialNumVisibleJobs = component.getNumVisibleJobs();
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
      expect(component.getNumVisibleJobs()).toBe(initialNumVisibleJobs);
    });

  /* Row detail expand tests */

    function getNumVisibleJobDetails() {
      const detailRows =
        fixture.debugElement.nativeElement.querySelectorAll(
          '.job-detail-row'
        );
      let numVisible = 0;
      for (const detailRow of detailRows) {
        if (detailRow.offsetHeight > 2) {
          ++numVisible;
        }
      }
      return numVisible;
    }

    it('Test visibility of expanded detail row.', function(done) {
      const jobDetailClickLayers =
        fixture.debugElement.nativeElement.querySelectorAll(
        '.job-detail-click-layer'
      );

      expect(component.expandedElement).toBeUndefined();
      expect(getNumVisibleJobDetails()).toBe(0);

      jobDetailClickLayers[0].dispatchEvent(new Event('click'));
      fixture.detectChanges();

      setTimeout(function() {
        expect(component.expandedElement).toBeDefined();
        expect(getNumVisibleJobDetails()).toBe(1);
        done();
      }, 250);
    });

    it('Test that row can be expanded and then collapsed again.', () => {
      const jobDetailClickLayers =
        fixture.debugElement.nativeElement.querySelectorAll(
        '.job-detail-click-layer'
      );

      expect(component.expandedElement).toBeUndefined();

      jobDetailClickLayers[0].dispatchEvent(new Event('click'));
      expect(component.expandedElement).toBeDefined();

      jobDetailClickLayers[0].dispatchEvent(new Event('click'));
      expect(component.expandedElement).toBeNull();
    });

    it('Test that only one job detail is expanded at any given time.',
      function(done) {
      const jobDetailClickLayers =
        fixture.debugElement.nativeElement.querySelectorAll(
        '.job-detail-click-layer'
      );

      expect(component.expandedElement).toBeUndefined();
      expect(getNumVisibleJobDetails()).toBe(0);

      for (const clickLayer of jobDetailClickLayers) {
        clickLayer.dispatchEvent(new Event('click'));
      }
      fixture.detectChanges();

      setTimeout(function() {
        expect(component.expandedElement).toBeDefined();
        expect(getNumVisibleJobDetails()).toBe(1);
        done();
      }, 250);
    });

    it('Test that a checkbox click will not cause a row expand.', () => {
      const tableCheckboxes =
        fixture.debugElement.nativeElement.querySelectorAll(
        '.mat-checkbox'
      );
      tableCheckboxes[0].dispatchEvent(new Event('click'));

      expect(component.expandedElement).toBeUndefined();
    });
  });
  describe('Pagination tests.', function () {
    const MOCK_NUM_JOBS = 100;

    // Pagination tests need getJobs RPC calls to be mocked differently than
    // other unit tests.
    function getRandomJobs(queryStart, queryLimit) {
      const jobs = [];
      let lastTimestamp = Date.now();
      // 50 hours
      const timeOffset = 172800;
      const numJobsToCreate = Math.min(queryLimit, MOCK_NUM_JOBS - queryStart)
      for (let i = 0; i < numJobsToCreate; i++) {
        const mockJob = new Job();
        mockJob.setJobId(i);
        mockJob.setName('Job' + i.toString());
        mockJob.setPriority((Math.floor(Math.random() * 100) % 4));
        lastTimestamp = lastTimestamp + Math.floor(timeOffset * Math.random());
        const startTimestamp = lastTimestamp + ( timeOffset * Math.random() / 20 );
        const finishedTimestamp = startTimestamp + ( timeOffset * Math.random() / 5 );
        mockJob.setCreatedTimeSecUtc(lastTimestamp);
        mockJob.setStartTimeSecUtc(startTimestamp);
        mockJob.setFinishedTimeSecUtc(finishedTimestamp);
        mockJob.setStatus(Math.floor(Math.random() * 100) % 7 );
        jobs.push(mockJob);
      }
      return jobs;
    }

    beforeEach(() => {
      fixture = TestBed.createComponent(ViewJobsComponent);
      component = fixture.componentInstance;
      // @ts-ignore
      getJobsSpy = spyOn<any>(component.moblabGrpcService, 'getJobs').and.callFake(function(callback, pageIndex, pageSize) {
        const mockJobs = getRandomJobs(pageIndex, pageSize);
        component.assignJobs(mockJobs);
      });

      // @ts-ignore
      getNumJobsSpy = spyOn<any>(component.moblabGrpcService, 'getNumJobs').and.callFake(function() {
          component.numJobs = MOCK_NUM_JOBS;
        });
      fixture.detectChanges();
    });

    it('Test pagination from start to end to start of jobs list.', () => {
      const pageNextButton =
        fixture.debugElement.nativeElement.querySelector(
          '.mat-paginator-navigation-next'
        );
      const pagePrevButton =
        fixture.debugElement.nativeElement.querySelector(
          '.mat-paginator-navigation-previous'
        );

      expect(pageNextButton.disabled).toBe(false);
      expect(pagePrevButton.disabled).toBe(true);

      // Going forwards in pages.
      for (let i = 0; i < MOCK_NUM_JOBS / component.paginator.pageSize - 2; i++) {
        pageNextButton.dispatchEvent(new Event('click'));
        expect(component.jobs.data.length).toBe(component.paginator.pageSize);
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
      for (let i = 0; i < MOCK_NUM_JOBS / component.paginator.pageSize - 2; i++) {
        pagePrevButton.dispatchEvent(new Event('click'));
        expect(component.jobs.data.length).toBe(component.paginator.pageSize);
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
