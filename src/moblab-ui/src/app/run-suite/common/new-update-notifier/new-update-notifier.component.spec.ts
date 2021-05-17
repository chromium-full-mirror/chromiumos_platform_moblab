import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewUpdateNotifierComponent } from './new-update-notifier.component';

describe('NewUpdateNotifierComponent', () => {
  let component: NewUpdateNotifierComponent;
  let fixture: ComponentFixture<NewUpdateNotifierComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ NewUpdateNotifierComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(NewUpdateNotifierComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
