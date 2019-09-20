import {Component, OnInit} from '@angular/core';
import {GlobalInfoService} from 'app/services/services.module';
import {Feature} from 'app/services/services.module';

@Component({
  selector: 'app-sidebar',
  templateUrl: './app-sidebar.component.html',
  styleUrls: ['./app-sidebar.component.scss']
})
export class AppSidebarComponent implements OnInit {
  appErrorMessage = 'This is where error messages go';

  navTabsAboveRun = [];
  navTestRunMenuOptions = [];
  navTabsBelowRun = [];

  constructor(private globalInfo: GlobalInfoService) {
    this.globalInfo = globalInfo;

    this.addSidebarEntry(
        Feature.VIEW_JOBS, this.navTabsAboveRun,
        {route: '/view_jobs', label: 'View Jobs', icon: 'visibility'});

    this.addSidebarEntry(
        Feature.RUN_CTS, this.navTestRunMenuOptions,
        {route: '/run_tests/cts', label: 'Android Qualification'});
    this.addSidebarEntry(
        Feature.RUN_STORAGE_QUAL, this.navTestRunMenuOptions,
        {route: '/run_tests/storagequal', label: 'Storage Qualification'});
    this.addSidebarEntry(
        Feature.RUN_MEMORY_QUAL, this.navTestRunMenuOptions,
        {route: '/run_tests/memoryqual', label: 'Memory Qualification'});
    this.addSidebarEntry(
        Feature.RUN_BOARD_QUAL, this.navTestRunMenuOptions,
        {route: '/run_tests/bvt', label: 'Board Qualification'});
    this.addSidebarEntry(
        Feature.RUN_POWER, this.navTestRunMenuOptions,
        {route: '/run_tests/power', label: 'Power'});
    this.addSidebarEntry(
        Feature.RUN_TESTS, this.navTestRunMenuOptions,
        {route: '/run_tests/other', label: 'Run Suite'});

    this.addSidebarEntry(Feature.DUT_MANAGEMENT, this.navTabsBelowRun, {
      route: '/manage_dut',
      label: 'Manage DUT\'s',
      icon: 'laptop_chromebook'
    });
    this.addSidebarEntry(
        Feature.SYSTEM_CONFIGURATION, this.navTabsBelowRun,
        {route: '/config', label: 'Configuration', icon: 'settings'});
    this.addSidebarEntry(
        Feature.MOBMONITOR, this.navTabsBelowRun,
        {route: '/mobmonitor', label: 'Mobmonitor', icon: 'security'});
    this.addSidebarEntry(Feature.ADVANCED_SETTINGS, this.navTabsBelowRun, {
      route: '/advanced',
      label: 'Advanced Settings',
      icon: 'settings_applications'
    });
    this.addSidebarEntry(Feature.REPORT_A_PROBLEM, this.navTabsBelowRun, {
      route: '/report_problem',
      label: 'Report Problem',
      icon: 'bug_report'
    });
    this.addSidebarEntry(
        Feature.DOCUMENTATION, this.navTabsBelowRun,
        {route: '/documentation', label: 'Documentation', icon: 'help'});
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

  ngOnInit() {}

  onSend(event) {
    console.log(event);
  }
}
