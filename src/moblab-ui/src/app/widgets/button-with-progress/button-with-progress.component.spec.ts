import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {ButtonWithProgressComponent} from './button-with-progress.component';

describe('ButtonWithProgressComponent', () => {
  let component: ButtonWithProgressComponent;
  let fixture: ComponentFixture<ButtonWithProgressComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ButtonWithProgressComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ButtonWithProgressComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
