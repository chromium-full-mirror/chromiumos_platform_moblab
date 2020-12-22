import {DatePipe} from '@angular/common';

function convertToSecondsTimestamp(timestamp: number) {
  if (isNaN(timestamp)) {
    throw new Error(['Invalid timestamp', timestamp].join(' '));
  }

  return Number(
    timestamp.toString().substring(0, timestamp.toString().length - 3)
  );
}

function convertToMilisecondsTimestamp(timestamp: number) {
  if (isNaN(timestamp)) {
    throw new Error(['Invalid timestamp', timestamp].join(' '));
  }

  const digits_count = timestamp.toString().length;
  if (digits_count === 10) {
    timestamp *= 1000;
  } else if (digits_count === 16) {
    timestamp /= 1000;
  }
  return timestamp;
}

// Because timestamps may be returned in second, millisecond, or nanosecond
// granularity, but Angular expects timestamps in milliseconds.
export function normalizeTimestamp(timestamp) {
  if (timestamp === 0) {
    return 'N/A';
  }

  timestamp = convertToMilisecondsTimestamp(timestamp);
  return new DatePipe('en-US').transform(
    new Date(timestamp),
    'yyyy-MM-dd HH:mm:ss'
  );
}

export function datestringToSecondsTimestamp(datestring) {
  const date = new Date(datestring);
  return isNaN(date.getTime())
    ? undefined
    : convertToSecondsTimestamp(date.getTime());
}
