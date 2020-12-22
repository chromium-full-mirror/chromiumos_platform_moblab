/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {MatCardModule} from '@angular/material/card';

import {LoadingOverlayComponent} from './loading-overlay.component';
import {MatProgressBarModule} from '@angular/material/progress-bar';

describe('LoadingOverlayComponent', () => {
  let component: LoadingOverlayComponent;
  let fixture: ComponentFixture<LoadingOverlayComponent>;

  function isOverlayVisible() {
    fixture.detectChanges();
    const overlays = fixture.debugElement.nativeElement.querySelectorAll(
      '#overlay'
    );
    return overlays.length !== 0;
  }

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [LoadingOverlayComponent],
      imports: [MatCardModule, MatProgressBarModule],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LoadingOverlayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('overlay defaults to hidden', () => {
    expect(isOverlayVisible()).toBeFalsy();
  });

  it('update call reveals overlay', () => {
    component.updateStatus('submitting');
    expect(isOverlayVisible()).toBeTruthy();
  });

  it('update call will change status message', () => {
    component.updateStatus('staging');
    fixture.detectChanges();
    component.updateStatus('submitting');
    fixture.detectChanges();

    const status_message_elt = fixture.debugElement.nativeElement.querySelector(
      '#loading-message'
    );

    expect(status_message_elt.textContent).toContain('submitting');
  });
});
