import {DutTask, Job} from '../services/moblabrpc_pb';

function createInvertedObj (obj) {
  const inverted_mappings = {};
  for (const key of Object.keys(obj)) {
    inverted_mappings[obj[key]] = key;
  }
  return inverted_mappings;
}

export const INT_TO_JOBSTATUS = createInvertedObj(Job.JobStatus);
export const INT_TO_PRIORITY = createInvertedObj(Job.Priority);
export const INT_TO_DUT_TASK_STATUS = createInvertedObj(DutTask.Status);
