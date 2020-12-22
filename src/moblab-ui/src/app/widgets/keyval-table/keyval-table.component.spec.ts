import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {FormsModule} from '@angular/forms';
import {MatSelectModule} from '@angular/material/select';
import {MatTableModule} from '@angular/material/table';

import {KeyValTableComponent} from './keyval-table.component';

describe('KeyValTableComponent', () => {
  let component: KeyValTableComponent;
  let fixture: ComponentFixture<KeyValTableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [FormsModule, MatSelectModule, MatTableModule],
      declarations: [KeyValTableComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(KeyValTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('row loading and empty check work.', () => {
    expect(component.isEmpty()).toBe(true);

    component.loadRows([
      ['key1', 'val1'],
      ['key2', 'val2'],
    ]);

    expect(component.isEmpty()).toBe(false);
  });
});
