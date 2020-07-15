/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {CommonModule} from '@angular/common';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {HttpClientModule} from '@angular/common/http';
import {MatCardModule} from '@angular/material/card';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatListModule} from '@angular/material/list';
import {MatPaginatorModule} from '@angular/material/paginator';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatSnackBarModule} from '@angular/material/snack-bar';

import {ConfigurationComponent} from './configuration.component';
import {RebootButtonComponent} from '../widgets/reboot-button/reboot-button';
import {MatDialogModule} from '@angular/material/dialog';


describe('ConfigurationComponent', () => {
  let component: ConfigurationComponent;
  let fixture: ComponentFixture<ConfigurationComponent>;

  let getNetworkInfoSpy: jasmine.Spy;
  let getVersionInfoSpy: jasmine.Spy;
  let getCloudConfigurationSpy: jasmine.Spy;
  let getDutWifiInfoSpy: jasmine.Spy;

  function inputConfiguration(inputIdentifier: string, input: string) {
    const inputEl = fixture.debugElement.nativeElement.querySelector(
      '#' + inputIdentifier
    );
    inputEl.value = input;
    inputEl.dispatchEvent(new Event('input'));
    fixture.detectChanges();
  }

  beforeEach(async(() => {
    TestBed.configureTestingModule({
        imports: [
          BrowserAnimationsModule,
          CommonModule,
          FormsModule,
          HttpClientModule,
          MatCardModule,
          MatDialogModule,
          MatFormFieldModule,
          MatIconModule,
          MatInputModule,
          MatListModule,
          MatPaginatorModule,
          MatProgressSpinnerModule,
          MatProgressSpinnerModule,
          MatSnackBarModule,
          ReactiveFormsModule,
        ],
        declarations: [
          ConfigurationComponent,
          RebootButtonComponent
        ]})
      .compileComponents();
  }));
  beforeEach(() => {
    fixture = TestBed.createComponent(ConfigurationComponent);
    component = fixture.componentInstance;

    getNetworkInfoSpy = spyOn<any>(component, 'getNetworkInfo').and.callFake(
      function() {
        component.setNetworkInfo(
          '000.000.000.000',
          true
        )
      });

    getVersionInfoSpy = spyOn<any>(component, 'getVersionInfo').and.callFake(
      function() {
        component.setVersionInfo(
          'R00-00000.00.0',
          'mock-release',
          'Mock description.',
          'xxxxxxxxxxxxxxxxxxxxxx',
          'XXXXXXXXXXXX'
        )
      });

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('network and version info populated on init', () => {
    expect(component.moblabHostname).toBeTruthy();
    expect(component.chromeosReleaseVersion).toBeTruthy();
    expect(component.chromeosReleaseDescription).toBeTruthy();
    expect(component.chromeosReleaseTrack).toBeTruthy();
  });

  it('empty configuration fields show error', () => {
    const errorItems = fixture.debugElement.nativeElement.querySelectorAll(
      '.mat-error'
    );

    expect(errorItems.length).toBe(3);
    expect(component.botoKeyIDForm.hasError('required')).toBeTruthy();
    expect(component.botoKeySecretForm.hasError('required')).toBeTruthy();
    expect(component.bucketURLForm.hasError('required')).toBeTruthy();
  });

  it('bad GCS URL shows error', () => {
    inputConfiguration('botoKeyIdInput', 'fake-boto-key');
    inputConfiguration('botoKeySecretInput', 'fake-secret-key');
    inputConfiguration('imageStorageUrlInput', 'gs://xxx/');

    expect(fixture.debugElement.nativeElement.querySelectorAll(
      '.mat-error'
    ).length).toBe(0);

    inputConfiguration('imageStorageUrlInput', 'gs:/xxx/');
    expect(fixture.debugElement.nativeElement.querySelectorAll(
      '.mat-error'
    ).length).toBe(1);

    inputConfiguration('imageStorageUrlInput', 'gs://xxx');
    expect(fixture.debugElement.nativeElement.querySelectorAll(
      '.mat-error'
    ).length).toBe(1);
  });

  it('good GCS URL shows link', () => {
    inputConfiguration('imageStorageUrlInput', 'gs://xxx/');
    expect(fixture.debugElement.nativeElement.querySelector(
      '#link-on-icon'
    )).toBeTruthy();
    expect(fixture.debugElement.nativeElement.querySelector(
      '#link-off-icon'
    )).toBeFalsy();
  });

  it('bad GCS URL does not show link', () => {
    inputConfiguration('imageStorageUrlInput', 'xxx');
    expect(fixture.debugElement.nativeElement.querySelector(
      '#link-on-icon'
    )).toBeFalsy();
    expect(fixture.debugElement.nativeElement.querySelector(
      '#link-off-icon'
    )).toBeTruthy();
  });

  describe('configuration set tests', function () {
    const MOCK_NUM_JOBS = 100;

    beforeEach(() => {
      fixture = TestBed.createComponent(ConfigurationComponent);
      component = fixture.componentInstance;
      getCloudConfigurationSpy = spyOn<any>(component, 'getCloudConfiguration').and.callFake(
        function() {
          component.setCloudConfiguration(
            'fake-boto-key',
            'fake-secret-key',
            'gs://xxx/',
          )
        });
      getDutWifiInfoSpy = spyOn<any>(component, 'getDutWifiInfo').and.callFake(
        function() {
          // ts-ignore
          component.setDutWifiInfo(
            'fake-wifi-name',
            'fake-wifi-pass',
          )
        });
      fixture.detectChanges();
    });

    it('cloud submit button only enabled on diff', () => {
      expect(fixture.debugElement.nativeElement.querySelector(
        '#cloud-config-submit-button'
      ).disabled).toBeTruthy();

      inputConfiguration('imageStorageUrlInput', 'gs://xxxx/');
      fixture.detectChanges();
      expect(fixture.debugElement.nativeElement.querySelector(
        '#cloud-config-submit-button'
      ).disabled).toBeFalsy();

      inputConfiguration('imageStorageUrlInput', 'gs://xxx/');
      fixture.detectChanges();
      expect(fixture.debugElement.nativeElement.querySelector(
        '#cloud-config-submit-button'
      ).disabled).toBeTruthy();
    });

    it('dut wifi info submit button only enabled on diff', () => {
      expect(fixture.debugElement.nativeElement.querySelector(
        '#dut-wifi-info-submit-button'
      ).disabled).toBeTruthy();

      inputConfiguration('dutWifiNameInput', 'fake-wifi-nam');
      fixture.detectChanges();
      expect(fixture.debugElement.nativeElement.querySelector(
        '#dut-wifi-info-submit-button'
      ).disabled).toBeFalsy();

      inputConfiguration('dutWifiNameInput', 'fake-wifi-name');
      fixture.detectChanges();
      expect(fixture.debugElement.nativeElement.querySelector(
        '#dut-wifi-info-submit-button'
      ).disabled).toBeTruthy();
    });
  });
});
