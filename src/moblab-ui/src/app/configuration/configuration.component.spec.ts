/* tslint:disable:no-unused-variable */
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';

import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {CommonModule} from '@angular/common';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {HttpClientModule} from '@angular/common/http';
import {MatCardModule} from '@angular/material/card';
import {MatDialogModule} from '@angular/material/dialog';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatListModule} from '@angular/material/list';
import {MatPaginatorModule} from '@angular/material/paginator';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatSnackBarModule} from '@angular/material/snack-bar';

import {ConfigurationComponent} from './configuration.component';
import {RebootButtonComponent} from '../widgets/reboot-button/reboot-button.component';

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
        MatSnackBarModule,
        ReactiveFormsModule,
      ],
      declarations: [ConfigurationComponent, RebootButtonComponent],
    }).compileComponents();
  }));
  beforeEach(() => {
    fixture = TestBed.createComponent(ConfigurationComponent);
    component = fixture.componentInstance;

    getNetworkInfoSpy = spyOn<any>(component, 'getNetworkInfo').and.callFake(
      () => {
        component.setNetworkInfo('000.000.000.000', true);
      }
    );

    getVersionInfoSpy = spyOn<any>(component, 'getVersionInfo').and.callFake(
      () => {
        component.refreshShownVersionInfo(
          'R00-00000.00.0',
          'mock-release',
          'Mock description.',
          'xxxxxxxxxxxxxxxxxxxxxx',
          'XXXXXXXXXXXX'
        );
      }
    );

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

  function isFormReadonly(formId: string) {
    const formElement = fixture.debugElement.nativeElement.querySelector(
      '#' + formId
    );
    return formElement.getAttribute('readonly') === 'true';
  }

  function toggleCheckbox(checkboxId: string) {
    fixture.debugElement
      .query(By.css('#' + checkboxId))
      .triggerEventHandler('change', new Event('change'));
    fixture.detectChanges();
  }

  function triggerCheckboxHoverStart(checkboxId: string) {
    fixture.debugElement
      .query(By.css('#' + checkboxId))
      .triggerEventHandler('mouseenter', new Event('mouseenter'));
    fixture.detectChanges();
  }

  function triggerCheckboxHoverStop(checkboxId: string) {
    fixture.debugElement
      .query(By.css('#' + checkboxId))
      .triggerEventHandler('mouseleave', new Event('mouseleave'));
    fixture.detectChanges();
  }

  it('cloud forms readonly when enable cloud is unchecked', () => {
    // enable cloud checkbox starts unchecked.
    expect(isFormReadonly('boto-key-id-input')).toBeTrue();
    expect(isFormReadonly('boto-key-secret-input')).toBeTrue();
    expect(isFormReadonly('image-storage-url-input')).toBeTrue();
  });

  it('cloud forms not readonly when enable cloud is checked', () => {
    toggleCheckbox('cloud-checkbox');

    expect(isFormReadonly('boto-key-id-input')).toBeFalse();
    expect(isFormReadonly('boto-key-secret-input')).toBeFalse();
    expect(isFormReadonly('image-storage-url-input')).toBeFalse();
  });

  it('remote console integration disabled by default when cloud is enabled', () => {
    toggleCheckbox('cloud-checkbox');

    expect(component.isRemoteConsoleEnabled).toBe(false);
  });

  it('cloud forms cleared once enable cloud is unchecked', () => {
    toggleCheckbox('cloud-checkbox');
    inputConfiguration('image-storage-url-input', 'gs://xxx');
    toggleCheckbox('cloud-checkbox');

    expect(
      fixture.debugElement.nativeElement.querySelector(
        '#image-storage-url-input'
      ).value
    ).toBe('');
  });

  it('empty configuration fields show error', () => {
    expect(component.botoKeyIDForm.hasError('required')).toBeTruthy();
    expect(component.botoKeySecretForm.hasError('required')).toBeTruthy();
    expect(component.bucketURLForm.hasError('required')).toBeTruthy();
  });

  it('bad GCS URL shows error', () => {
    inputConfiguration('boto-key-id-input', 'fake-boto-key');
    inputConfiguration('boto-key-secret-input', 'fake-secret-key');
    inputConfiguration('image-storage-url-input', 'gs://xxx/');

    expect(component.bucketURLForm.hasError('notAGSUrl')).toBeFalse();

    inputConfiguration('image-storage-url-input', 'gs:/xxx/');
    console.log(component.bucketURLForm.hasError('notAGSUrl'));
    expect(component.bucketURLForm.hasError('notAGSUrl')).toBeTrue();
  });

  it('hover over cloud checkbox will show clear warnings', () => {
    toggleCheckbox('cloud-checkbox');

    inputConfiguration('boto-key-id-input', 'fake-boto-key');
    inputConfiguration('boto-key-secret-input', 'fake-secret-key');
    inputConfiguration('image-storage-url-input', 'gs://xxx/');

    triggerCheckboxHoverStart('cloud-checkbox');

    expect(component.botoKeyIDForm.hasError('clearWarning')).toBeTruthy();
    expect(component.botoKeySecretForm.hasError('clearWarning')).toBeTruthy();
    expect(component.bucketURLForm.hasError('clearWarning')).toBeTruthy();
  });

  it('clear warnings will be go away once user mouses-off checkbox', () => {
    toggleCheckbox('cloud-checkbox');

    inputConfiguration('boto-key-id-input', 'fake-boto-key');

    triggerCheckboxHoverStart('cloud-checkbox');
    expect(component.botoKeyIDForm.hasError('clearWarning')).toBeTrue();

    triggerCheckboxHoverStop('cloud-checkbox');
    expect(component.botoKeyIDForm.hasError('clearWarning')).toBeFalse();

    // sequence below verifies that 'clear' warnings are removed even if mouse-off
    // happens after cloud checkbox is unchecked.
    triggerCheckboxHoverStart('cloud-checkbox');
    expect(component.botoKeyIDForm.hasError('clearWarning')).toBeTrue();
    toggleCheckbox('cloud-checkbox');
    triggerCheckboxHoverStop('cloud-checkbox');
    expect(component.botoKeyIDForm.hasError('clearWarning')).toBeFalse();
  });

  it('hover start and stop wont clear formatting warnings', () => {
    toggleCheckbox('cloud-checkbox');

    inputConfiguration('image-storage-url-input', 'gs:/malformed');

    expect(component.bucketURLForm.hasError('notAGSUrl')).toBeTrue();

    triggerCheckboxHoverStart('cloud-checkbox');
    triggerCheckboxHoverStop('cloud-checkbox');

    expect(component.bucketURLForm.hasError('notAGSUrl')).toBeTrue();
  });

  it('good GCS URL shows link', () => {
    inputConfiguration('image-storage-url-input', 'gs://xxx/');
    expect(
      fixture.debugElement.nativeElement.querySelector('#link-on-icon')
    ).toBeTruthy();
    expect(
      fixture.debugElement.nativeElement.querySelector('#link-off-icon')
    ).toBeFalsy();
  });

  it('bad GCS URL does not show link', () => {
    inputConfiguration('image-storage-url-input', 'xxx');
    expect(
      fixture.debugElement.nativeElement.querySelector('#link-on-icon')
    ).toBeFalsy();
    expect(
      fixture.debugElement.nativeElement.querySelector('#link-off-icon')
    ).toBeTruthy();
  });

  describe('configuration set tests', () => {
    const MOCK_NUM_JOBS = 100;

    beforeEach(() => {
      fixture = TestBed.createComponent(ConfigurationComponent);
      component = fixture.componentInstance;
      getCloudConfigurationSpy = spyOn<any>(
        component,
        'getCloudConfiguration'
      ).and.callFake(() => {
        component.updateCloudConfigurationForms(
          'fake-boto-key',
          'fake-secret-key',
          'gs://xxx/',
          true,
          true,
          true
        );
      });
      getDutWifiInfoSpy = spyOn<any>(component, 'getDutWifiInfo').and.callFake(
        () => {
          // @ts-ignore
          component.setDutWifiInfo('fake-wifi-name', 'fake-wifi-pass');
        }
      );
      fixture.detectChanges();
    });

    it('cloud submit button only enabled on diff', () => {
      expect(
        fixture.debugElement.nativeElement.querySelector(
          '#cloud-config-submit-button'
        ).disabled
      ).toBeTruthy();

      inputConfiguration('image-storage-url-input', 'gs://xxxx/');
      fixture.detectChanges();
      expect(
        fixture.debugElement.nativeElement.querySelector(
          '#cloud-config-submit-button'
        ).disabled
      ).toBeFalsy();

      inputConfiguration('image-storage-url-input', 'gs://xxx/');
      fixture.detectChanges();
      expect(
        fixture.debugElement.nativeElement.querySelector(
          '#cloud-config-submit-button'
        ).disabled
      ).toBeTruthy();
    });

    it('dut wifi info submit button only enabled on diff', () => {
      expect(
        fixture.debugElement.nativeElement.querySelector(
          '#dut-wifi-info-submit-button'
        ).disabled
      ).toBeTruthy();

      inputConfiguration('dut-wifi-name-input', 'fake-wifi-nam');
      fixture.detectChanges();
      expect(
        fixture.debugElement.nativeElement.querySelector(
          '#dut-wifi-info-submit-button'
        ).disabled
      ).toBeFalsy();

      inputConfiguration('dut-wifi-name-input', 'fake-wifi-name');
      fixture.detectChanges();
      expect(
        fixture.debugElement.nativeElement.querySelector(
          '#dut-wifi-info-submit-button'
        ).disabled
      ).toBeTruthy();
    });

    it('dut wifi has to be non-empty', () => {
      inputConfiguration('dut-wifi-name-input', '');
      fixture.detectChanges();
      expect(
        fixture.debugElement.nativeElement.querySelector(
          '#dut-wifi-info-submit-button'
        ).disabled
      ).toBeTruthy();
    });

    it('dut wifi has to have no leading/trailing whitespace', () => {
      inputConfiguration('dut-wifi-name-input', ' wifi-name');
      fixture.detectChanges();
      expect(
        fixture.debugElement.nativeElement.querySelector(
          '#dut-wifi-info-submit-button'
        ).disabled
      ).toBeTruthy();
    });

    it('dut wifi password can be empty', () => {
      inputConfiguration('dut-wifi-name-input', 'wifi-name');
      inputConfiguration('dut-wifi-password-input', '');
      fixture.detectChanges();
      expect(
        fixture.debugElement.nativeElement.querySelector(
          '#dut-wifi-info-submit-button'
        ).disabled
      ).toBeFalsy();
    });
  });
});
