/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {FormsModule, ReactiveFormsModule} from '@angular/forms';

import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {By} from '@angular/platform-browser';
import {CommonModule} from '@angular/common';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatDividerModule} from '@angular/material/divider';
import {MatExpansionModule} from '@angular/material/expansion';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatTableModule} from '@angular/material/table';
import {RouterModule} from '@angular/router';

import {JobDetailComponent} from './job-detail.component';
import {Job, Execution} from '../services/moblabrpc_pb';
import {ViewJobsModule} from '../view-jobs/view-jobs.module';
import {WidgetsModule} from '../widgets/widgets.module';

function createMockJobInfo() {
  const mockJob = new Job();
  mockJob.setJobId(1);
  mockJob.setName('Name');
  mockJob.setServerControlFile('Fake file.');

  const mockJobHistory = [];
  for (let i = 0; i < 5; ++i) {
    const mockExecution = new Execution();
    mockExecution.setName(i.toString());
    mockExecution.setJobId(i);
    mockExecution.setUsedTime(Number(Math.random() * 1000));
    mockJobHistory.push(mockExecution);
  }
  mockJob.setExecutionHistoryList(mockJobHistory);

  const mockAssociatedDuts = [];
  for (let i = 0; i < 5; ++i) {
    const mockExecution = new Execution();
    mockExecution.setDut(i.toString());
    mockExecution.setStatus(Number(Math.random() * 8));
    mockAssociatedDuts.push(mockExecution);
  }
  mockJob.setAssociatedDutsList(mockJobHistory);

  return mockJob;
}

describe('JobDetailComponent', () => {
  let component: JobDetailComponent;
  let fixture: ComponentFixture<JobDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        CommonModule,
        FormsModule,
        MatButtonModule,
        MatCardModule,
        MatDividerModule,
        MatExpansionModule,
        MatFormFieldModule,
        MatInputModule,
        MatTableModule,
        MatSnackBarModule,
        ReactiveFormsModule,
        RouterModule,
        RouterModule.forRoot([]),
        ViewJobsModule,
        WidgetsModule,
      ],
      declarations: [JobDetailComponent],
    }).compileComponents();
  }));

  function inputJobQuery(val) {
    const jobQueryInput = fixture.debugElement.nativeElement.querySelector(
      '#job-query-input'
    );
    jobQueryInput.value = val;
    jobQueryInput.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  describe('Success case tests.', () => {
    beforeEach(() => {
      fixture = TestBed.createComponent(JobDetailComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();

      const childJobsRefSpy = spyOn<any>(
        component.childViewJobsTableRef,
        'refreshJobs'
      );
      const getJobDetailsSpy = spyOn<any>(
        // @ts-ignore
        component.moblabGrpcService,
        'getJobDetails'
      ).and.callFake(
        (
          callback: (x: Job) => void,
          errorHandlingCallback: (errorMsg: string) => void,
          id: string
        ) => {
          component.unpackJobInfoToTable(createMockJobInfo());
        }
      );
    });

    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('cannot query invalid job id.', () => {
      const jobQueryButton = fixture.debugElement.nativeElement.querySelector(
        '#job-query-button'
      );
      expect(jobQueryButton.disabled).toBeTruthy();

      inputJobQuery('NaN');
      expect(jobQueryButton.disabled).toBeTruthy();

      inputJobQuery('1');
      expect(jobQueryButton.disabled).toBeFalsy();
    });

    it('successful load of job information.', () => {
      let jobDetailTableRows = fixture.debugElement.nativeElement.querySelectorAll(
        '#job-detail-table .mat-row'
      );

      let jobHistoryTableRows = fixture.debugElement.nativeElement.querySelectorAll(
        '#job-execution-history-table .mat-row'
      );

      let associatedDutsTableRows = fixture.debugElement.nativeElement.querySelectorAll(
        '#associated-duts-table .mat-row'
      );

      // Loading overlay is visible before a job is loaded.
      expect(
        fixture.debugElement.query(By.css('#loading-overlay'))
      ).toBeDefined();
      expect(component.jobInfoTableRef.isEmpty()).toBe(true);

      inputJobQuery('1');
      const jobQueryButton = fixture.debugElement.nativeElement.querySelector(
        '#job-query-button'
      );
      jobQueryButton.dispatchEvent(new Event('click'));
      fixture.detectChanges();

      jobDetailTableRows = fixture.debugElement.nativeElement.querySelectorAll(
        '#job-detail-table .mat-row'
      );

      jobHistoryTableRows = fixture.debugElement.nativeElement.querySelectorAll(
        '#job-execution-history-table .mat-row'
      );

      associatedDutsTableRows = fixture.debugElement.nativeElement.querySelectorAll(
        '#associated-duts-table .mat-row'
      );

      // Loading overlay is gone after a job is loaded.
      expect(fixture.debugElement.query(By.css('#loading-overlay'))).toBeNull();
      expect(component.jobInfoTableRef.isEmpty()).toBe(false);
      expect(jobHistoryTableRows.length > 0).toBeTruthy();
      expect(associatedDutsTableRows.length > 0).toBeTruthy();
    });
  });

  describe('Failure case tests.', () => {
    beforeEach(() => {
      fixture = TestBed.createComponent(JobDetailComponent);
      component = fixture.componentInstance;

      const getJobDetailsSpy = spyOn<any>(
        // @ts-ignore
        component.moblabGrpcService,
        'getJobDetails'
      ).and.callFake(
        (
          callback: (x: Job) => void,
          errorHandlingCallback: (errorMsg: string) => void,
          id: string
        ) => {
          errorHandlingCallback('Error message');
        }
      );
    });

    it('failure of job information load is handled correctly.', () => {
      // Loading overlay is visible before a job is loaded.
      expect(
        fixture.debugElement.query(By.css('#loading-overlay'))
      ).toBeDefined();

      inputJobQuery('9999');
      const jobQueryButton = fixture.debugElement.nativeElement.querySelector(
        '#job-query-button'
      );
      jobQueryButton.dispatchEvent(new Event('click'));
      fixture.detectChanges();

      // After a failed job query, job details section of page is still greyed
      // out.
      expect(
        fixture.debugElement.query(By.css('#loading-overlay'))
      ).toBeDefined();
    });
  });
});
