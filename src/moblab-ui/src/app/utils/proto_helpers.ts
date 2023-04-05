import {
  ConnectedDutInfo,
  DutTask,
  Job,
  RunStorageQualificationSuiteRequest,
} from '../services/moblabrpc_pb';

export const BUILD_STATUS_MAPPINGS: {[key: number]: string} = {
  0: 'Passed',
  1: 'Failed',
  2: 'Running',
  3: 'Aborted',
  4: 'Recommended',
};

const DUT_STATUS_MAPPINGS: {[key: string]: string} = {
  DUT_STATUS_UNKNOWN: 'Unknown',
  DUT_STATUS_READY: 'Ready',
  DUT_STATUS_RUNNING: 'Running',
  DUT_STATUS_REPAIRING: 'Repairing',
  DUT_STATUS_REPAIR_FAILED: 'Repair Failed',
  DUT_STATUS_CLEANING: 'Cleaning',
  DUT_STATUS_PENDING: 'Pending',
  DUT_STATUS_RESETTING: 'Resetting',
  DUT_STATUS_PROVISIONING: 'Provisioning',
  DUT_STATUS_VERIFYING: 'Verifying',
  DUT_STATUS_DISCONNECTED: 'Disconnected',
  DUT_STATUS_NOT_ENROLLED: 'Not Enrolled',
};

function invertAndMap(obj, new_mappings) {
  /**
   * Invert the provided object and map it to the provided mappings.
   */
  const readble_dut_states = {};
  for (const key of Object.keys(obj)) {
    readble_dut_states[obj[key]] = new_mappings[key];
  }
  return readble_dut_states;
}

export const INT_TO_DUT_STATUS = invertAndMap(
  ConnectedDutInfo.DutStatus,
  DUT_STATUS_MAPPINGS
);

function createInvertedObj(obj) {
  const inverted_mappings = {};
  for (const key of Object.keys(obj)) {
    inverted_mappings[obj[key]] = key;
  }
  return inverted_mappings;
}

export const INT_TO_JOBUPLOADSTATUS = createInvertedObj(Job.UploadStatus);
export const INT_TO_JOBSTATUS = createInvertedObj(Job.JobStatus);
export const INT_TO_PRIORITY = createInvertedObj(Job.Priority);
export const INT_TO_DUT_TASK_STATUS = createInvertedObj(DutTask.Status);
export const INT_TO_STORAGE_QUAL_VARIATION = createInvertedObj(
  RunStorageQualificationSuiteRequest.Variation
);
