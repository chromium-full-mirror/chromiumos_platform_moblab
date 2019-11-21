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
import { WidgetsModule } from "../widgets/widgets.module";
import {By} from '@angular/platform-browser';

import { Job } from '../services/moblabrpc_pb';
import { ViewJobsComponent } from './view-jobs.component';
import { CHECKBOX_ID } from '../widgets/table-header-selector/table-header-selector.component';

const NUM_MOCK_JOBS = 20;

function mockJobs(numJobs) {
  const arr = [];
  // const numJobs = 20;
  let lastTimestamp = Date.now();
  // 50 hours
  let timeOffset = 172800;
  for (var i = 0; i < numJobs; i++) {
    let mockJob = new Job();
    mockJob.setJobId(i);
    mockJob.setName('Job' + i.toString());
    mockJob.setPriority((Math.floor(Math.random() * 100) % 4));
    lastTimestamp = lastTimestamp + Math.floor(timeOffset * Math.random());
    const startTimestamp = lastTimestamp + ( timeOffset * Math.random() / 20 );
    const finishedTimestamp = startTimestamp + ( timeOffset * Math.random() / 5 );
    mockJob.setCreatedTimeSecUtc(lastTimestamp);
    mockJob.setStartTimeSecUtc(startTimestamp);
    mockJob.setFinishedTimeSecUtc(finishedTimestamp);
    mockJob.setStatus(Math.floor(i / ( numJobs / 7 )));
    arr.push(mockJob);
  }
  return arr;
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
          WidgetsModule
        ],
        declarations: [
          ViewJobsComponent]})
        .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ViewJobsComponent);
    component = fixture.componentInstance;
    // @ts-ignore
    spyOn<any>(component.moblabGrpcService, 'getJobs').and.callFake(function() {
              component.jobs.data = mockJobs(NUM_MOCK_JOBS);
            });

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it ('jobs loaded in', () => {
    expect(component.getNumJobs() === NUM_MOCK_JOBS).toBeTruthy();
  });

  //////////////////////////////////////////////////// Checkbox tests ////////////////////////////////////////////////////
  it('no jobs checked initially', () => {
    expect(component.getNumSelectedJobs() === 0).toBeTruthy();
  });

  it ('check all then uncheck all', () => {
    const selectJobsButton = fixture.debugElement.nativeElement.querySelector('#' + CHECKBOX_ID);
    expect(component.getNumSelectedJobs() === 0).toBeTruthy();
    selectJobsButton.dispatchEvent(new Event('change'));
    expect(component.getNumSelectedJobs() === NUM_MOCK_JOBS).toBeTruthy();
    selectJobsButton.dispatchEvent(new Event('change'));
    expect(component.getNumSelectedJobs() === 0).toBeTruthy();
  });

  it ('check one job, then check all jobs', () => {
    const selectJobsButton = fixture.debugElement.nativeElement.querySelector('#' + CHECKBOX_ID);
    component.job_selections.select(component.jobs.data[0]);
    expect(component.getNumSelectedJobs() === 1).toBeTruthy();
    selectJobsButton.dispatchEvent(new Event('change'));
    expect(component.getNumSelectedJobs() === NUM_MOCK_JOBS).toBeTruthy();
  });

  it ('check all jobs, then uncheck one job, then uncheck all jobs, then check all jobs', () => {
    const selectJobsButton = fixture.debugElement.nativeElement.querySelector('#' + CHECKBOX_ID);
    selectJobsButton.dispatchEvent(new Event('change'));
    expect(component.getNumSelectedJobs() === NUM_MOCK_JOBS).toBeTruthy();
    component.job_selections.deselect(component.jobs.data[0]);
    expect(component.getNumSelectedJobs() === NUM_MOCK_JOBS - 1).toBeTruthy();
    selectJobsButton.dispatchEvent(new Event('change'));
    expect(component.getNumSelectedJobs() === 0).toBeTruthy();
    selectJobsButton.dispatchEvent(new Event('change'));
    expect(component.getNumSelectedJobs() === NUM_MOCK_JOBS).toBeTruthy();
  });

  it ('multi single select', () => {
    component.job_selections.select(component.jobs.data[0]);
    expect(component.getNumSelectedJobs() === 1).toBeTruthy();
    component.job_selections.select(component.jobs.data[1]);
    expect(component.getNumSelectedJobs() === 2).toBeTruthy();
  });

  //////////////////////////////////////////////////// Refresh tests ////////////////////////////////////////////////////
  it ('refresh test', function(done) {
    // @ts-ignore
    expect(component.moblabGrpcService.getJobs).toHaveBeenCalledTimes(1);
    const refreshButton = fixture.debugElement.nativeElement.querySelector('.job-refresh-button');
    refreshButton.dispatchEvent(new Event('click'));
    // @ts-ignore
    expect(component.moblabGrpcService.getJobs).toHaveBeenCalledTimes(2);
    setTimeout(function() {
      // Because the RPC call to get jobs has been mocked out, we know it will 'return' in less than .5 sec, the check
      // below is to ensure that jobs are not duplicated on refresh calls.
      expect(component.getNumJobs() === NUM_MOCK_JOBS).toBeTruthy();
      done();
    }, 500);

  })
});
