import {Component, OnInit} from '@angular/core';
import {GlobalInfoService} from 'app/services/services.module';
import {MoblabSettingsService} from 'app/services/moblab-settings.service';
import {ConfigSetupService} from '../services/moblab-configuration-alerting.service';
import {Feature} from 'app/services/services.module';
import {MoblabSettingsConstains} from '../constants';

@Component({
  selector: 'app-sidebar',
  templateUrl: './app-sidebar.component.html',
  styleUrls: ['./app-sidebar.component.scss'],
})
export class AppSidebarComponent implements OnInit {
  appErrorMessage = 'This is where error messages go';

  // TODO(crbug.com/1111126) Reference actual Dockerfile var for these port numbers
  // (so we don't hardcode these numbers in multiple places)
  mobmonitor_port = '9991';

  mobmonitor_link = this._format_mobmonitor_link(
    window.location.hostname,
    this.mobmonitor_port
  );

  navTabs = [];
  navTestRunMenuOptions = [];
  pauseRequestors = [];
  showCloudConfigWarning = false;

  constructor(
    private globalInfo: GlobalInfoService,
    private settingsService: MoblabSettingsService,
    private configSetupService: ConfigSetupService,
  ) {
    this.addSidebarEntry(Feature.DUT_MANAGEMENT, this.navTabs, {
      route: '/manage_dut',
      label: "Manage DUTs",
      icon: 'laptop_chromebook',
    });
    this.addSidebarEntry(Feature.DUT_DETAIL, this.navTabs, {
      route: '/dut_detail',
      label: 'DUT Detail',
    });
    this.addSidebarEntry(Feature.RUN_TESTS, this.navTabs, {
      route: '/run_tests',
      label: 'Run Suite',
      icon: 'play_arrow',
    });
    this.addSidebarEntry(Feature.VIEW_JOBS, this.navTabs, {
      route: '/view_jobs',
      label: 'View Jobs',
      icon: 'visibility',
    });
    this.addSidebarEntry(Feature.JOB_DETAIL, this.navTabs, {
      route: '/job_detail',
      label: 'Job Detail',
    });
    this.addSidebarEntry(Feature.SYSTEM_CONFIGURATION, this.navTabs, {
      route: '/config',
      label: 'Configuration',
      icon: 'settings',
    });
    this.addSidebarEntry(Feature.MOBMONITOR, this.navTabs, {
      route: '/mobmonitor',
      label: 'Mobmonitor',
      icon: 'security',
    });
    this.addSidebarEntry(Feature.ADVANCED_SETTINGS, this.navTabs, {
      route: '/advanced',
      label: 'Advanced Settings',
      icon: 'settings_applications',
    });
    this.addSidebarEntry(Feature.REPORT_A_PROBLEM, this.navTabs, {
      route: '/report_problem',
      label: 'Report Problem',
      icon: 'bug_report',
    });
    this.addSidebarEntry(Feature.DOCUMENTATION, this.navTabs, {
      route: '/documentation',
      label: 'Documentation',
      icon: 'help',
    });
  }

  getErrors() {
    return [];
  }

  getMessages() {
    return [];
  }

  isPageInformationEnabled() {
    return this.isFeatureEnabled(Feature.TOOLBAR_PAGE_INFORMATION);
  }

  isFeedbackEnabled() {
    return this.isFeatureEnabled(Feature.FEEDBACK_REPORTS);
  }

  isFeatureEnabled(feature: Feature) {
    return this.globalInfo.isFeatureEnabled(feature);
  }
  addSidebarEntry(feature: Feature, entryList, sidebarEntry) {
    if (this.isFeatureEnabled(feature)) {
      entryList.push(sidebarEntry);
    }
  }

  _format_afe_link(hostname: string, port: string) {
    return `http://${hostname}:${port}/afe`;
  }

  _format_mobmonitor_link(hostname: string, port: string) {
    return `http://${hostname}:${port}/static/index.html`;
  }

  ngOnInit(): void {
    this.settingsService.pauseRequestorsObservable.subscribe(requestors => {
      this.pauseRequestors = requestors;
    });
    this.configSetupService.cloudConfigObservable.subscribe(enabled => {
      this.showCloudConfigWarning = !enabled;
    });
  }

  getPausedDueToUser(): string[] {
    return this.pauseRequestors.filter(
      p => p === MoblabSettingsConstains.USER_REQUEST_STRING
    );
  }

  getPausedDueToLowDisk(): string[] {
    return this.pauseRequestors.filter(
      p => p === MoblabSettingsConstains.LOW_DISK_SPACE_STRING
    );
  }
}
