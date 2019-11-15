import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { LayoutModule } from '@angular/cdk/layout';
import {
  MatButtonModule,
  MatCardModule,
  MatFormFieldModule,
  MatIconModule,
  MatListModule,
  MatMenuModule,
  MatSidenavModule,
  MatTabsModule,
  MatToolbarModule,
} from '@angular/material';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { AppSidebarComponent } from './app-sidebar.component';
import { GlobalInfoService, ServicesModule } from 'app/services/services.module';

describe('AppSidebarComponent', () => {
  let component: AppSidebarComponent;
  let fixture: ComponentFixture<AppSidebarComponent>;

  beforeEach(async(() => {
    TestBed
        .configureTestingModule({
          declarations: [
            AppSidebarComponent,
          ],
          imports: [
            FormsModule,
            LayoutModule,
            MatButtonModule,
            MatCardModule,
            MatFormFieldModule,
            MatIconModule,
            MatListModule,
            MatListModule,
            MatMenuModule,
            MatSidenavModule,
            MatTabsModule,
            MatToolbarModule,
            NoopAnimationsModule,
            ServicesModule
          ],
          providers: [
            {provide: GlobalInfoService, useClass: GlobalInfoService}
          ],
          schemas: [
            NO_ERRORS_SCHEMA
          ]
        })
        .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AppSidebarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should compile', () => {
    expect(component).toBeTruthy();
  });
});
