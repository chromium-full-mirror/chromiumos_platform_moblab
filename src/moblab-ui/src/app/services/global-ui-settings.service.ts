import {Injectable} from '@angular/core';

enum UIState {
  NEEDS_SETUP = 1,
  SETUP_COMPLETE,
  NO_DUTS_CONFIGURED,
};

export enum Feature {
  VIEW_JOBS = 1,
  RUN_CTS,
  RUN_STORAGE_QUAL,
  RUN_MEMORY_QUAL,
  RUN_BOARD_QUAL,
  RUN_FSI,
  RUN_TESTS,
  RUN_POWER,
  DUT_MANAGEMENT,
  SYSTEM_CONFIGURATION,
  ADVANCED_SETTINGS,
  REPORT_A_PROBLEM,
  MOBMONITOR,
  DOCUMENTATION,
  FEEDBACK_REPORTS,
  TOOLBAR_PAGE_INFORMATION,
  JOB_DETAIL,
  DUT_DETAIL
}
;

@Injectable()
export class GlobalInfoService {
  enabledFeatures = [
    Feature.DUT_MANAGEMENT,
    Feature.FEEDBACK_REPORTS,
    Feature.RUN_TESTS,
    Feature.VIEW_JOBS,
    Feature.JOB_DETAIL,
    Feature.DUT_DETAIL,
    Feature.SYSTEM_CONFIGURATION
  ];

  constructor() {};

  getUIState() {
    return UIState.NEEDS_SETUP;
  };
  isFeatureEnabled(f: Feature) {
    return this.enabledFeatures.indexOf(f) > -1;
  };
}
