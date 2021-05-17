export class MoblabSettingsConstains {
  static readonly USER_REQUEST_STRING = 'User request';
  static readonly LOW_DISK_SPACE_STRING = 'Low disk space';
}
export class MoblabHealthCheckConstants {
  static readonly MOBLAB_CONTAINERS_COUNT = 13;
}

export enum NewUpdateStatus {
  UNKNOWN,
  NO_UPDATE,
  UPDATE_AVAILABLE,
  UPDATE_AVAILABLE_WITH_JOBS_RUNNING,
}
