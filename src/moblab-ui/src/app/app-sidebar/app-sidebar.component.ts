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

  navTabs = [];
  navTestRunMenuOptions = [];

  constructor(private globalInfo: GlobalInfoService) {
    this.globalInfo = globalInfo;
    this.addSidebarEntry(
      Feature.DUT_MANAGEMENT, this.navTabs, {
        route: '/manage_dut', label: 'Manage DUT\'s', icon: 'laptop_chromebook'});
    this.addSidebarEntry(
      Feature.DUT_DETAIL, this.navTabs,
      {route: '/dut_detail', label: 'DUT Detail'});
    this.addSidebarEntry(
      Feature.RUN_TESTS, this.navTabs,
      {route: '/run_tests', label: 'Run Suite', icon: 'play_arrow'});
    this.addSidebarEntry(
      Feature.VIEW_JOBS, this.navTabs,
        {route: '/view_jobs', label: 'View Jobs', icon: 'visibility'});
    this.addSidebarEntry(
      Feature.JOB_DETAIL, this.navTabs,
      {route: '/job_detail', label: 'Job Detail'});
    this.addSidebarEntry(
        Feature.SYSTEM_CONFIGURATION, this.navTabs,
        {route: '/config', label: 'Configuration', icon: 'settings'});
    this.addSidebarEntry(
        Feature.MOBMONITOR, this.navTabs,
        {route: '/mobmonitor', label: 'Mobmonitor', icon: 'security'});
    this.addSidebarEntry(Feature.ADVANCED_SETTINGS, this.navTabs, {
      route: '/advanced',
      label: 'Advanced Settings',
      icon: 'settings_applications'
    });
    this.addSidebarEntry(Feature.REPORT_A_PROBLEM, this.navTabs, {
      route: '/report_problem',
      label: 'Report Problem',
      icon: 'bug_report'
    });
    this.addSidebarEntry(
        Feature.DOCUMENTATION, this.navTabs,
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
