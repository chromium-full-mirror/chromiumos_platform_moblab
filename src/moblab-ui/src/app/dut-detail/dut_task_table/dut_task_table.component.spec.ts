import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {CommonModule} from '@angular/common';
import {DutTaskTableComponent} from './dut_task_table.component';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatDividerModule} from '@angular/material/divider';
import {MatExpansionModule} from '@angular/material/expansion';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatPaginatorModule} from '@angular/material/paginator';
import {MatTableModule} from '@angular/material/table';

import {DutTask} from '../../services/moblabrpc_pb';
import {ViewJobsModule} from '../../view-jobs/view-jobs.module';
import {WidgetsModule} from '../../widgets/widgets.module';

const NUM_MOCK_TASKS = 100;

function createMockDutTasks() {
  const mockDutTasks = [];

  for (let i = 0; i < NUM_MOCK_TASKS; i++) {
    const mockDutTask = new DutTask();
    mockDutTask.setId(i);
    mockDutTask.setTask('Mock Task');
    mockDutTask.setStatus(Math.floor(Math.random() * 5));
    mockDutTask.setCreatedTimeUtc(Math.floor(Date.now() / 1000));
    mockDutTasks.push(mockDutTask);
  }
  return mockDutTasks;
}

describe('DutTaskTableComponent', () => {
  let component: DutTaskTableComponent;
  let fixture: ComponentFixture<DutTaskTableComponent>;

  let getDutTasksSpy: jasmine.Spy;
  let getNumDutTasksSpy: jasmine.Spy;

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
        ViewJobsModule,
        WidgetsModule,
      ],
      declarations: [DutTaskTableComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DutTaskTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DutTaskTableComponent);
    component = fixture.componentInstance;
    // @ts-ignore
    getDutTasksSpy = spyOn<any>(
      component.moblabGrpcService,
      'getDutTasks'
    ).and.callFake(() => {
      component.setDutTasks(createMockDutTasks());
    });

    // @ts-ignore
    getNumDutTasksSpy = spyOn<any>(
      component.moblabGrpcService,
      'getNumDutTasks'
    ).and.callFake(() => {
      component.numDutTasks = createMockDutTasks().length;
    });
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('setting DUT IP should initialize table', () => {
    component.setDutIp('000.000.000.000');
    fixture.detectChanges();
    expect(component.tasks.data.length).toBe(createMockDutTasks().length);
    fixture.detectChanges();
    component.getNextPageDutTasks();
    expect(component.tasks.data.length).toBe(createMockDutTasks().length);
  });
});
