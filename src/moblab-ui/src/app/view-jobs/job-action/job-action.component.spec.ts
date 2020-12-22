import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {By} from '@angular/platform-browser';
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {FormsModule} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatSelect, MatSelectModule} from '@angular/material/select';
import {MatSnackBarModule} from '@angular/material/snack-bar';

import {Job} from '../../services/moblabrpc_pb';
import {JobActionComponent} from './job-action.component';

function getMockJob(jobId) {
  const mockJob = new Job();
  mockJob.setName('Job' + jobId);
  mockJob.setJobId(jobId);
  return mockJob;
}

describe('JobActionComponent', () => {
  let component: JobActionComponent;
  let fixture: ComponentFixture<JobActionComponent>;

  let abortJobsSpy: jasmine.Spy;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        FormsModule,
        MatButtonModule,
        MatCardModule,
        MatFormFieldModule,
        MatSelectModule,
        MatSnackBarModule,
      ],
      declarations: [JobActionComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(JobActionComponent);
    component = fixture.componentInstance;
    // @ts-ignore
    abortJobsSpy = spyOn<any>(component.moblabGrpcService, 'abortJobs');
    fixture.detectChanges();
  });

  function applySelection(selectionValue) {
    fixture.debugElement.query(
      By.directive(MatSelect)
    ).componentInstance.value = selectionValue;
    component.selectedAction = selectionValue;
    fixture.detectChanges();
  }

  function clickActionButton() {
    const actionButton = fixture.debugElement.nativeElement.querySelector(
      '#action-button'
    );
    actionButton.dispatchEvent(new Event('click'));
    fixture.detectChanges();
  }

  it('should create.', () => {
    expect(component).toBeTruthy();
  });

  it('component is disabled without both job + action select.', () => {
    const actionButton = fixture.debugElement.nativeElement.querySelector(
      '#action-button'
    );
    applySelection('Abort');
    expect(actionButton.disabled).toBeTruthy();
    applySelection('');
    component.selectJob(getMockJob(0));
    fixture.detectChanges();
    expect(actionButton.disabled).toBeTruthy();
  });

  it('action button enables after action select + job select.', () => {
    applySelection('Abort');
    component.selectJob(getMockJob(0));
    fixture.detectChanges();
    const actionButton = fixture.debugElement.nativeElement.querySelector(
      '#action-button'
    );
    expect(actionButton.disabled).toBeFalsy();
  });

  it('call of abort jobs works.', () => {
    applySelection('Abort');
    component.selectJob(getMockJob(0));
    fixture.detectChanges();
    clickActionButton();
    expect(abortJobsSpy).toHaveBeenCalled();
  });

  it('job selection clears after action submit.', () => {
    expect(component.getNumSelectedJobs()).toBe(0);

    applySelection('Abort');
    component.selectJob(getMockJob(0));
    fixture.detectChanges();

    expect(component.getNumSelectedJobs()).toBe(1);
    clickActionButton();
    expect(component.getNumSelectedJobs()).toBe(0);
  });
});
