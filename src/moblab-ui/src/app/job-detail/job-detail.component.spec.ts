/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import {CommonModule} from '@angular/common';
import {
  FormsModule,
  ReactiveFormsModule
} from '@angular/forms';
import {
  MatButtonModule,
  MatTableModule,
} from '@angular/material';
import {MatCardModule} from '@angular/material/card';
import {MatDividerModule} from '@angular/material/divider';
import {MatExpansionModule} from '@angular/material/expansion';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {By} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import {JobDetailComponent} from './job-detail.component';
import {Job} from '../services/moblabrpc_pb';


function createMockJobInfo() {
  const mockJob = new Job();
  mockJob.setJobId(1);
  mockJob.setName('Name');
  mockJob.setServerControlFile('Fake file.');
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
          ReactiveFormsModule,
          MatButtonModule,
          MatCardModule,
          MatDividerModule,
          MatExpansionModule,
          MatFormFieldModule,
          MatInputModule,
          MatTableModule,
          MatSnackBarModule
        ],
        declarations: [JobDetailComponent]})
      .compileComponents();
  }));

  function inputJobQuery(val) {
    const jobQueryInput = fixture.debugElement.nativeElement.querySelector(
      '#job-query-input'
    );
    jobQueryInput.value = val;
    jobQueryInput.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  describe('Success case tests.', function () {
    beforeEach(() => {
      fixture = TestBed.createComponent(JobDetailComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();

      const getJobDetailsSpy = spyOn<any>(
        // @ts-ignore
        component.moblabGrpcService,
        'getJobDetails'
      ).and.callFake(
        (callback: (x: Job) => void,
         errorHandlingCallback: (errorMsg: string) => void,
         id: string) => {
          component.unpackJobInfoToTable(createMockJobInfo())
        });
    });

    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('Test cannot query invalid job id.', () => {
      const jobQueryButton = fixture.debugElement.nativeElement.querySelector(
        '#job-query-button'
      );
      expect(jobQueryButton.disabled).toBeTruthy();

      inputJobQuery('NaN');
      expect(jobQueryButton.disabled).toBeTruthy();

      inputJobQuery('1');
      expect(jobQueryButton.disabled).toBeFalsy();
    });

    it('Test successful load of job information.', () => {
      let jobDetailTableRows =
        fixture.debugElement.nativeElement.querySelectorAll(
        '#job-detail-table .mat-row'
      );

      // Loading overlay is visible before a job is loaded.
      expect(fixture.debugElement.query(
        By.css('#loading-overlay'))).toBeDefined();
      expect(jobDetailTableRows.length).toBe(0);

      inputJobQuery('1');
      const jobQueryButton = fixture.debugElement.nativeElement.querySelector(
        '#job-query-button'
      );
      jobQueryButton.dispatchEvent(new Event('click'));
      fixture.detectChanges();

      jobDetailTableRows = fixture.debugElement.nativeElement.querySelectorAll(
        '#job-detail-table .mat-row'
      );

      // Loading overlay is gone after a job is loaded.
      expect(fixture.debugElement.query(
        By.css('#loading-overlay'))).toBeNull();
      expect(jobDetailTableRows.length > 0 ).toBeTruthy();
    });
  });

  describe('Failure case tests.', function () {
    beforeEach(() => {
      fixture = TestBed.createComponent(JobDetailComponent);
      component = fixture.componentInstance;

      const getJobDetailsSpy = spyOn<any>(
        // @ts-ignore
        component.moblabGrpcService,
        'getJobDetails'
      ).and.callFake(
        (callback: (x: Job) => void,
         errorHandlingCallback: (errorMsg: string) => void,
         id: string) => {
          errorHandlingCallback('Error message');
        });
    });

    it('Test failure of job information load.', () => {
      // Loading overlay is visible before a job is loaded.
      expect(fixture.debugElement.query(
        By.css('#loading-overlay'))).toBeDefined();

      inputJobQuery('9999');
      const jobQueryButton = fixture.debugElement.nativeElement.querySelector(
        '#job-query-button'
      );
      jobQueryButton.dispatchEvent(new Event('click'));
      fixture.detectChanges();

      // After a failed job query, job details section of page is still greyed
      // out.
      expect(fixture.debugElement.query(
        By.css('#loading-overlay'))).toBeDefined();
    });
  });
});
