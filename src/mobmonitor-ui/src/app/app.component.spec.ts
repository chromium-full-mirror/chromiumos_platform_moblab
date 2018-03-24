import { TestBed, ComponentFixture, async } from '@angular/core/testing';
import { Component } from '@angular/core';
import { By } from '@angular/platform-browser';
import { of } from 'rxjs/observable/of';

import { AppComponent } from './app.component';
import { MobmonitorRpcService } from './services/mobmonitor-rpc.service';

@Component({selector: 'mob-health-checks', template: ''})
class HealthChecksStubComponent {}

describe('AppComponent', () => {
  let component: AppComponent;
  let fixture: ComponentFixture<AppComponent>;

  beforeEach(async(() => {
    const rpcSpy = jasmine.createSpyObj('MobmonitorRpcService', ['getStatus']);
    rpcSpy.getStatus.and.returnValue(of([]));
    TestBed.configureTestingModule({
      declarations: [
        AppComponent,
        HealthChecksStubComponent
      ],
      providers: [
        {provide: MobmonitorRpcService, useValue: rpcSpy}
      ]
    }).compileComponents();
  }));
  beforeEach(() => {
    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create the app', () => {
    expect(component).toBeTruthy();
  });

  it('should update the time', () => {
      const p = fixture.debugElement.query(By.css('p')).nativeElement;
      const dateText = p.textContent.replace('last updated ', '');
      expect(new Date(dateText)).toBeTruthy();
  });

});
