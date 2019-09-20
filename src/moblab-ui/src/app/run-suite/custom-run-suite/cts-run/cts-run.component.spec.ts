import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {CtsRunComponent} from './cts-run.component';

describe('CtsRunComponent', () => {
  let component: CtsRunComponent;
  let fixture: ComponentFixture<CtsRunComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({declarations: [CtsRunComponent]})
        .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CtsRunComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
