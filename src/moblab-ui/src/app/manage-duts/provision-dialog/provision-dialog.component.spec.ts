import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProvisionDialogComponent } from './provision-dialog.component';

describe('ProvisionDialogComponent', () => {
  let component: ProvisionDialogComponent;
  let fixture: ComponentFixture<ProvisionDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ProvisionDialogComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ProvisionDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
