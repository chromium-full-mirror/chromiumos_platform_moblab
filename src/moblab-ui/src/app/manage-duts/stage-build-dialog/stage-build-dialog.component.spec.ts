import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StageBuildDialogComponent } from './stage-build-dialog.component';

describe('StageBuildDialogComponent', () => {
  let component: StageBuildDialogComponent;
  let fixture: ComponentFixture<StageBuildDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ StageBuildDialogComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(StageBuildDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
