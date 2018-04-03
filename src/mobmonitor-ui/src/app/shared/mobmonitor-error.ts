export interface MobmonitorError {
    message: string;
    body: any;
    stacktrace: string;
}

/**
Wraps an arbitrary type of error in a Mobmonitor error

@param error error to wrap
@param message user friendly message
@return a MobmonitorError object
*/
export function wrapError(error: any, message: string): MobmonitorError {
  const err = new Error();
  return {
    body: error,
    message,
    stacktrace: err.stack
  };
}
