/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {By} from '@angular/platform-browser';
import {DebugElement} from '@angular/core';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatIconModule} from '@angular/material/icon';
import {MatTableModule} from '@angular/material/table';
import {RouterModule} from '@angular/router';

import {
  ConnectedDutInfo,
  Job,
  ListConnectedDutsResponse,
} from '../../services/moblabrpc_pb';
import {PipesModule} from 'app/pipes/pipes.module';
import {ViewDutsComponent} from './view-duts.component';
import {WidgetsModule} from 'app/widgets/widgets.module';

function createMockDuts(): ConnectedDutInfo[] {
  const mockDuts = [];
  for (let i = 0; i < 10; i++) {
    for (let j = 0; j < 2; j++) {
      const mockDut = new ConnectedDutInfo();
      mockDut.setName('MockDUT' + i.toString());
      mockDut.setIp('000.000.000.00' + i.toString());
      mockDut.setStatus('FakeStatus');
      mockDut.setIsEnrolled(j ? true : false);
      mockDuts.push(mockDut);
    }
  }
  return mockDuts;
}

describe('ViewDutsComponent', () => {
  let component: ViewDutsComponent;
  let fixture: ComponentFixture<ViewDutsComponent>;
  let getDutsSpy: jasmine.Spy;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        MatCardModule,
        MatCheckboxModule,
        MatIconModule,
        MatTableModule,
        PipesModule,
        RouterModule,
        RouterModule.forRoot([]),
        WidgetsModule,
      ],
      declarations: [ViewDutsComponent],
    }).compileComponents();
  }));

  function applyClickTo(button_identifier: string) {
    const button = fixture.debugElement.nativeElement.querySelector(
      button_identifier
    );
    button.dispatchEvent(new Event('click'));
    fixture.detectChanges();
  }

  beforeEach(() => {
    fixture = TestBed.createComponent(ViewDutsComponent);
    component = fixture.componentInstance;

    getDutsSpy = spyOn<any>(
      component.moblabGrpcService,
      'listConnectedDuts'
    ).and.callFake(() => {
      component.assignDuts(createMockDuts());
    });

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('load-in case.', () => {
    const viewDutsTableRows = fixture.debugElement.nativeElement.querySelectorAll(
      '#view-duts-table .mat-row'
    );

    expect(viewDutsTableRows.length).toBe(createMockDuts().length);
    expect(getDutsSpy).toHaveBeenCalledTimes(1);
  });

  it('refresh button works.', () => {
    applyClickTo('#duts-refresh-button');

    const viewDutsTableRows = fixture.debugElement.nativeElement.querySelectorAll(
      '#view-duts-table .mat-row'
    );

    expect(viewDutsTableRows.length).toBe(createMockDuts().length);
    expect(getDutsSpy).toHaveBeenCalledTimes(2);
  });

  it('unenrolled DUTs can be hidden.', () => {
    component.setHideUnenrolledDuts(true);
    fixture.detectChanges();

    const viewDutsTableRows = fixture.debugElement.nativeElement.querySelectorAll(
      '#view-duts-table .mat-row'
    );
    let hiddenDutsCount = 0;
    viewDutsTableRows.forEach(row => {
      if (row.hidden) {
        hiddenDutsCount += 1;
      }
    });

    expect(hiddenDutsCount).toBe(viewDutsTableRows.length / 2);
  });

  it('select all and select no DUTs toggles correctly.', () => {
    expect(component.getSelectedDutHostnames().length).toBe(0);

    // Toggling checkbox widget.
    component.headerSelectorRef.checkboxChange();
    expect(component.getSelectedDutHostnames().length).toBe(
      createMockDuts().length
    );

    component.headerSelectorRef.checkboxChange();
    expect(component.getSelectedDutHostnames().length).toBe(0);
  });
});
