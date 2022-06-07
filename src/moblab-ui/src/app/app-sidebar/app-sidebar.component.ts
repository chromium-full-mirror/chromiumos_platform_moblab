import {Component, OnInit} from '@angular/core';
import {GlobalInfoService} from 'app/services/services.module';
import {MoblabSettingsService} from 'app/services/moblab-settings.service';
import {ConfigSetupService} from '../services/moblab-configuration-alerting.service';
import {BuildTargetAccessService} from 'app/services/build-target-access.service';
import {Feature} from 'app/services/services.module';
import {MoblabSettingsConstains, build_access_request_link} from '../constants';
import {MoblabRebootCheckService} from '../services/moblab-reboot-check.service';
import {
  Notification,
  NotificationsService,
} from 'app/services/notifications.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './app-sidebar.component.html',
  styleUrls: ['./app-sidebar.component.scss'],
})
export class AppSidebarComponent implements OnInit {
  readonly build_access_request_link = build_access_request_link;
  appErrorMessage = 'This is where error messages go';

  // TODO(crbug.com/1111126) Reference actual Dockerfile var for these port numbers
  // (so we don't hardcode these numbers in multiple places)
  mobmonitor_port = '9991';

  mobmonitor_link = this._format_mobmonitor_link(
    window.location.hostname,
    this.mobmonitor_port
  );
  enableNavBar: boolean;
  navTabs = [];
  navTestRunMenuOptions = [];
  pauseRequestors = [];
  cloudConfigEnabled: boolean;
  cloudConfigError: boolean;
  notificationsList: Notification[] = [];
  modelsWithoutAccess: string[] = [];
  moblabUptime: string;

  constructor(
    private globalInfo: GlobalInfoService,
    private settingsService: MoblabSettingsService,
    private configSetupService: ConfigSetupService,
    private notificationsService: NotificationsService,
    private buildTargetAccessService: BuildTargetAccessService,
    private rebootCheckService: MoblabRebootCheckService
  ) {
    this.addSidebarEntry(Feature.DUT_MANAGEMENT, this.navTabs, {
      route: '/manage_dut',
      label: 'Manage DUTs',
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
    this.addSidebarEntry(Feature.ABOUT, this.navTabs, {
      route: '/about',
      label: 'About',
      icon: 'info',
    });
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
    this.configSetupService.cloudConfigObservable.subscribe(data => {
      this.cloudConfigError = data['error'];
      if (this.cloudConfigError) {
        // Let user navigate through the UI when unable to retrieve cloud
        // configuration.
        this.cloudConfigEnabled = true;
      } else {
        this.cloudConfigEnabled = data['enabled'];
      }
    });
    this.globalInfo.enableNavBarObservable.subscribe(enabled => {
      this.enableNavBar = enabled;
    });
    this.notificationsService.notificationsObservable.subscribe(
      notifications => {
        this.notificationsList = notifications;
      }
    );
    this.buildTargetAccessService.modelsWithoutAccessObservable.subscribe(
      models => {
        this.modelsWithoutAccess = models;
      }
    );
    this.rebootCheckService.getMoblabUptime().then(
      uptime => {
        this.moblabUptime = uptime;
      },
      (errorMsg: string) => {
        console.log(
          'Encountered failure getting moblab timing info. ',
          errorMsg
        );
      }
    );
  }

  isSideNavEnabled(): boolean {
    return this.enableNavBar && this.cloudConfigEnabled;
  }

  getSideNavTooltip(): string {
    if (!this.enableNavBar) {
      return 'Disabled. Application is not ready yet!';
    }
    if (!this.cloudConfigEnabled) {
      return 'Disabled. Please provide a valid cloud configuration!';
    }
    return '';
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

  // Prevents unnecessary rerendering of the list,
  // which was cancelling click event on Dismiss button
  // on notification banners.
  trackByFn(_, item) {
    return item.notification;
  }

  dismissNotification(notification: Notification) {
    this.notificationsService.dismiss(notification.id);
  }
}
