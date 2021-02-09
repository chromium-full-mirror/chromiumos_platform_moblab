# -*- coding: utf-8 -*-
# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Basic infrastructure for implementing retries."""



import functools
import random
import re
import subprocess
import sys
import time

import six

import logging


# Match stderr of curl's --fail option to see HTTP status code.
CURL_STATUS_RE = re.compile(r'The requested URL returned error: (\d+) ')


def _CreateExceptionRetryHandler(exception):
  """Returns a retry handler for given exception(s).

  Please see WithRetry class document for details.
  """
  if not (isinstance(exception, type) and issubclass(exception, Exception) or
          (isinstance(exception, tuple) and
           all(issubclass(e, Exception) for e in exception))):
    raise TypeError('exceptions should be an exception (or tuple), not %r' %
                    exception)
  return lambda exc: isinstance(exc, exception)


class _RetryDelayStrategy(object):
  """The strategy of the delay between each retry attempts.

  Please see WithRetry class document for details.
  """

  def __init__(self, sleep=0, backoff_factor=1, jitter=0):
    if sleep < 0:
      raise ValueError('sleep must be >= 0: %s' % sleep)

    if backoff_factor < 1:
      raise ValueError('backoff_factor must be 1 or greater: %s'
                       % backoff_factor)

    if jitter < 0:
      raise ValueError('jitter must be >= 0: %s' % jitter)

    self._sleep = sleep
    self._backoff_factor = backoff_factor
    self._jitter = jitter

  def Sleep(self, attempt):
    """Sleep to delay the current retry."""
    assert attempt >= 1, 'Expect attempt is always positive: %s' % attempt
    if self._backoff_factor > 1:
      sleep_duration = self._sleep * self._backoff_factor ** (attempt - 1)
    else:
      sleep_duration = self._sleep * attempt

    # If |jitter| is set, add a random jitter sleep.
    jitter = random.uniform(.5 * self._jitter, 1.5 * self._jitter)
    total = sleep_duration + jitter
    if total:
      logging.debug('Retrying in %f (%f + jitter %f) seconds ...',
                    total, sleep_duration, jitter)
      time.sleep(total)


class WithRetry(object):
  """Decorator to handle retry on exception.

  Examples:
    @WithRetry(max_retry=3)
    def _run():
      ... do something ...
    _run()

    If _run() raises an exception, it retries at most three times.

  Retrying strategy.

  If the decorated function throws an Exception instance, then this class
  checks whether the retry should be continued or not based on the given
  |handler| or |exception| as follows.
  - If |handler| is given, which should be a callback which takes an exception
    and returns bool, calls it with the thrown exception.
    If the |handler| returns True, retry will be continued. Otherwise no
    further retry will be made, and an exception will be raised.
  - If |exception| is given, which is an exception class or a tuple of
    exception classes, iff the thrown exception is a instance of the given
    exception class(es) (or its subclass), continues to retry. Otherwise no
    further retry will be made, and an exception will be raised.
  - If neither is given, just continues to retry on any Exception instance.
  - Note: it is not allowed to specify both |handler| and |exception| at once.

  Delay strategy.

  Between for each attempt, some delay can be set, as follows.
  - If |sleep| is given, the delay between the first and second attempts is
    |sleep| secs.
  - The delay between the second and third attempts, and later, depends on
    |sleep| and |backoff_factor|.
    - If |backoff_factor| is not given, the delay will be linearly increased,
      as |sleep| * (number of attempts). E.g., if |sleep| is 1, the delays
      will be 1, 2, 3, 4, 5, ... and so on.
    - If |backoff_factor| is given, the delay will be exponentially increased,
      as |sleep| * |backoff_factor| ** (number of attempts - 1). E.g., if
      |sleep| is 1, and |backoff_factor| is 2, the delay will be,
      1, 2, 4, 8, 16, ... and so on
  - Note: Keep in mind that, if |backoff_factor| is not given, the total
    delay time will be triangular value of |max_retry| multiplied by the
    |sleep| value. E.g., |max_retry| is 5, and |sleep| is 10, will be
    T5 (i.e. 5 + 4 + 3 + 2 + 1) times 10 = 150 seconds total. Rather than
    use a large sleep value, you should lean more towards large retries
    and lower sleep intervals, or by utilizing |backoff_factor|.
  - In addition, for each delay, random duration of the delay can be added,
    as 'jitter'. (Often, this helps to avoid consecutive conflicting situation)
    |jitter| is specifies the duration of jitter delay, randomized up to
    50% in either direction.
  """

  def __init__(self,
               max_retry, handler=None, exception=None, log_all_retries=False,
               sleep=0, backoff_factor=1, jitter=0,
               raise_first_exception_on_failure=True, exception_to_raise=None,
               status_callback=None):
    """Initialize.

    Args:
      max_retry: A positive integer representing how many times to retry the
          command before giving up.  Worst case, the command is invoked
          (max_retry + 1) times before failing.
      handler: Please see above for details.
      exception: Please see above for details.
      log_all_retries: when True, logs all retries.
      sleep: Please see above for details.
      backoff_factor: Please see above for details.
      jitter: Please see above for details.
      raise_first_exception_on_failure: determines which excecption is raised
          upon failure after retries. If True, the first exception that was
          encountered. Otherwise, the final one.
      exception_to_raise: Optional exception type. If given, raises its
          instance, instead of the one raised from the retry body.
      status_callback: Optional callback invoked after each call of |functor|.
          It takes two arguments: |attempt| which is the index of the last
          attempt (0-based), and |success| representing whether the last attempt
          was successfully done or not. If the callback raises an exception, no
          further retry will be made, and the exception will be propagated to
          the caller.
    """
    if max_retry < 0:
      raise ValueError('max_retry needs to be zero or more: %d' % max_retry)
    self._max_retry = max_retry

    if handler is not None and exception is not None:
      raise ValueError('handler and exception cannot be specified at once')
    self._handler = (
        handler or _CreateExceptionRetryHandler(exception or Exception))

    self._log_all_retries = log_all_retries
    self._retry_delay = _RetryDelayStrategy(sleep, backoff_factor, jitter)
    self._raise_first_exception_on_failure = raise_first_exception_on_failure
    self._exception_to_raise = exception_to_raise
    self._status_callback = status_callback or (lambda attempt, success: None)

  def __call__(self, func):
    @functools.wraps(func)
    def _Wrapper(*args, **kwargs):
      fname = getattr(func, '__qualname__',
                      getattr(func, '__name__', '<nameless>'))
      exc_info = None
      for attempt in range(self._max_retry + 1):
        if attempt:
          self._retry_delay.Sleep(attempt)

        if attempt and self._log_all_retries:
          logging.debug('Retrying %s (attempt %d)', fname, attempt + 1)

        try:
          ret = func(*args, **kwargs)
        except Exception as e:
          # Note we're not snagging BaseException, so
          # MemoryError/KeyboardInterrupt and friends don't enter this except
          # block.

          # If raise_first_exception_on_failure, we intentionally ignore
          # any failures in later attempts since we'll throw the original
          # failure if all retries fail.
          if exc_info is None or not self._raise_first_exception_on_failure:
            exc_info = sys.exc_info()

          try:
            self._status_callback(attempt, False)
          except Exception:
            # In case callback raises an exception, quit the retry.
            # For further investigation, log the original exception here.
            logging.error('Ending retry due to Exception raised by a callback. '
                          'Original exception raised during the attempt is '
                          'as follows: ',
                          exc_info=exc_info)
            # Reraise the exception raised from the status_callback.
            raise

          if not self._handler(e):
            logging.debug('ending retries with error: %s(%s)', e.__class__, e)
            break
          logging.debug('%s(%s)', e.__class__, e)
        else:
          # Run callback in outside of try's main block, in order to avoid
          # accidental capture of an Exception which may be raised in callback.
          self._status_callback(attempt, True)
          return ret

      # Did not return, meaning all attempts failed. Raise the exception.
      if self._exception_to_raise:
        raise self._exception_to_raise('%s: %s' % (exc_info[0], exc_info[1]))
      six.reraise(exc_info[0], exc_info[1], exc_info[2])
    return _Wrapper


def GenericRetry(handler, max_retry, functor, *args, **kwargs):
  """Generic retry loop w/ optional break out depending on exceptions.

  Runs functor(*args, **(kwargs excluding params for retry)) as a retry body.

  Please see WithRetry for details about retrying parameters.
  """
  # Note: the default value needs to be matched with the ones of WithRetry's
  # ctor.
  log_all_retries = kwargs.pop('log_all_retries', False)
  delay_sec = kwargs.pop('delay_sec', 0)
  sleep = kwargs.pop('sleep', 0)
  backoff_factor = kwargs.pop('backoff_factor', 1)
  status_callback = kwargs.pop('status_callback', None)
  raise_first_exception_on_failure = kwargs.pop(
      'raise_first_exception_on_failure', True)
  exception_to_raise = kwargs.pop('exception_to_raise', None)

  @WithRetry(
      max_retry=max_retry, handler=handler, log_all_retries=log_all_retries,
      sleep=sleep, backoff_factor=backoff_factor, jitter=delay_sec,
      raise_first_exception_on_failure=raise_first_exception_on_failure,
      exception_to_raise=exception_to_raise,
      status_callback=status_callback)
  def _run():
    return functor(*args, **kwargs)
  return _run()


def RetryException(exception, max_retry, functor, *args, **kwargs):
  """Convenience wrapper for GenericRetry based on exceptions.

  Runs functor(*args, **(kwargs excluding params for retry)) as a retry body.

  Please see WithRetry for details about retrying parameters.
  """
  log_all_retries = kwargs.pop('log_all_retries', False)
  delay_sec = kwargs.pop('delay_sec', 0)
  sleep = kwargs.pop('sleep', 0)
  backoff_factor = kwargs.pop('backoff_factor', 1)
  status_callback = kwargs.pop('status_callback', None)
  raise_first_exception_on_failure = kwargs.pop(
      'raise_first_exception_on_failure', True)
  exception_to_raise = kwargs.pop('exception_to_raise', None)

  @WithRetry(
      max_retry=max_retry, exception=exception,
      log_all_retries=log_all_retries,
      sleep=sleep, backoff_factor=backoff_factor, jitter=delay_sec,
      raise_first_exception_on_failure=raise_first_exception_on_failure,
      exception_to_raise=exception_to_raise,
      status_callback=status_callback)
  def _run():
    return functor(*args, **kwargs)
  return _run()


def RetryCommand(functor, max_retry, *args, **kwargs):
  """Wrapper for run that will retry a command.

  Args:
    functor: run function to run; retries will only occur on
      RunCommandError exceptions being thrown.
    max_retry: A positive integer representing how many times to retry
      the command before giving up.  Worst case, the command is invoked
      (max_retry + 1) times before failing.
    sleep: Optional keyword.  Multiplier for how long to sleep between
      retries; will delay (1*sleep) the first time, then (2*sleep),
      continuing via attempt * sleep.
    retry_on: If provided, we will retry on any exit codes in the given list.
      Note: A process will exit with a negative exit code if it is killed by a
      signal. By default, we retry on all non-negative exit codes.
    error_check: Optional callback to check the error output.  Return None to
      fall back to |retry_on|, or True/False to set the retry directly.
    log_retries: Whether to log a warning when retriable errors occur.
    args: Positional args passed to run; see run for specifics.
    kwargs: Optional args passed to run; see run for specifics.

  Returns:
    A CommandResult object.

  Raises:
    RunCommandError: Raised on error.
  """
  values = kwargs.pop('retry_on', None)
  error_check = kwargs.pop('error_check', lambda x: None)
  log_retries = kwargs.pop('log_retries', True)

  def ShouldRetry(exc):
    """Return whether we should retry on a given exception."""
    if not ShouldRetryCommandCommon(exc):
      return False
    if values is None and exc.result.returncode < 0:
      logging.info('Child process received signal %d; not retrying.',
                   -exc.result.returncode)
      return False

    ret = error_check(exc)
    if ret is not None:
      return ret

    if values is None or exc.result.returncode in values:
      if log_retries:
        logging.warning('Command failed with retriable error.\n%s', exc)
      return True
    return False

  return GenericRetry(ShouldRetry, max_retry, functor, *args, **kwargs)


def ShouldRetryCommandCommon(exc):
  """Returns whether any run should retry on a given exception."""
  if exc.result.returncode is None:
    logging.error('Child process failed to launch; not retrying:\n'
                  'command: %s', exc.result.cmdstr)
    return False
  return True


def RunCommandWithRetries(max_retry, *args, **kwargs):
  """Wrapper for run that will retry a command

  Args:
    max_retry: See RetryCommand and run.
    *args: See RetryCommand and run.
    **kwargs: See RetryCommand and run.

  Returns:
    A CommandResult object.

  Raises:
    RunCommandError: Raised on error.
  """
  return RetryCommand(_run, max_retry, *args, **kwargs)


class DownloadError(Exception):
  """Fetching file via curl failed"""


def RunCurl(curl_args, *args, **kwargs):
  """Runs curl and wraps around all necessary hacks.

  Args:
    curl_args: Command line to pass to curl. Must be list of str.
    *args, **kwargs: See RunCommandWithRetries and run.
      Note that retry_on, error_check, sleep, backoff_factor cannot be
      overwritten.

  Returns:
    A CommandResult object.

  Raises:
    DownloadError: Whenever curl fails for any reason.
  """
  cmd = ['curl'] + curl_args

  # These values were discerned via scraping the curl manpage; they're all
  # retry related (dns failed, timeout occurred, etc, see  the manpage for
  # exact specifics of each).
  # Note we allow 22 to deal w/ 500's- they're thrown by google storage
  # occasionally.  This is also thrown when getting 4xx, but curl doesn't
  # make it easy to differentiate between them.
  # Note we allow 35 to deal w/ Unknown SSL Protocol error, thrown by
  # google storage occasionally.
  # Finally, we do not use curl's --retry option since it generally doesn't
  # actually retry anything; code 18 for example, it will not retry on.
  retriable_exits = frozenset([5, 6, 7, 15, 18, 22, 26, 28, 35, 52, 56])

  def _CheckExit(exc):
    """Filter out specific error codes when getting exit 22

    Curl will exit(22) for a wide range of HTTP codes -- both the 4xx and 5xx
    set.  For the 4xx, we don't want to retry.  We have to look at the output.
    """
    assert isinstance(exc, _runCommandError)
    if exc.result.returncode == 22:
      logging.debug('curl stderr %s', exc.result.error)
      matched = CURL_STATUS_RE.search(exc.result.error)
      if not matched:
        # Unexpected stderr.  It may not be error output from --fail.
        return True
      status_code = matched.group(1)
      return not status_code.startswith('4')

    # We'll let the common exit code filter do the right thing.
    return None

  try:
    return RunCommandWithRetries(
        10, cmd, retry_on=retriable_exits, error_check=_CheckExit,
        sleep=3, backoff_factor=1.6,
        stderr=True, extra_env={'LC_MESSAGES': 'C'}, *args, **kwargs)
  except _runCommandError as e:
    if e.result.returncode in (51, 58, 60):
      # These are the return codes of failing certs as per 'man curl'.
      raise DownloadError(
          'Download failed with certificate error? Try " c_rehash".')
    raise DownloadError('Curl failed w/ exit code %i: %s' %
                        (e.result.returncode, e.result.error))


# pylint: disable=redefined-builtin
def _run(cmd, print_cmd=True, stdout=None, stderr=None,
        cwd=None, input=None, enter_chroot=False,
        shell=False, env=None, extra_env=None, ignore_sigint=False,
        chroot_args=None, debug_level=logging.INFO,
        check=True, int_timeout=1, kill_timeout=1,
        log_output=False, capture_output=False,
        quiet=False, mute_output=None, encoding=None, errors=None, dryrun=False,
        **kwargs):
  """Runs a command.

  Args:
    cmd: cmd to run.  Should be input to subprocess.Popen. If a string, shell
      must be true. Otherwise the command must be an array of arguments, and
      shell must be false.
    print_cmd: prints the command before running it.
    stdout: Where to send stdout.  This may be many things to control
      redirection:
        * None is the default; the existing stdout is used.
        * An existing file object (must be opened with mode 'w' or 'wb').
        * A string to a file (will be truncated & opened automatically).
        * subprocess.PIPE to capture & return the output.
        * A boolean to indicate whether to capture the output.
          True will capture the output via a tempfile (good for large output).
        * An open file descriptor (as a positive integer).
    stderr: Where to send stderr.  See |stdout| for possible values.  This also
      may be subprocess.STDOUT to indicate stderr & stdout should be combined.
    cwd: the working directory to run this cmd.
    input: The data to pipe into this command through stdin.  If a file object
      or file descriptor, stdin will be connected directly to that.
    enter_chroot: this command should be run from within the chroot.  If set,
      cwd must point to the scripts directory. If we are already inside the
      chroot, this command will be run as if |enter_chroot| is False.
    shell: Controls whether we add a shell as a command interpreter.  See cmd
      since it has to agree as to the type.
    env: If non-None, this is the environment for the new process.  If
      enter_chroot is true then this is the environment of the enter_chroot,
      most of which gets removed from the cmd run.
    extra_env: If set, this is added to the environment for the new process.
      In enter_chroot=True case, these are specified on the post-entry
      side, and so are often more useful.  This dictionary is not used to
      clear any entries though.
    ignore_sigint: If True, we'll ignore signal.SIGINT before calling the
      child.  This is the desired behavior if we know our child will handle
      Ctrl-C.  If we don't do this, I think we and the child will both get
      Ctrl-C at the same time, which means we'll forcefully kill the child.
    chroot_args: An array of arguments for the chroot environment wrapper.
    debug_level: The debug level of run's output.
    check: Whether to raise an exception when command returns a non-zero exit
      code, or return the CommandResult object containing the exit code.
      Note: will still raise an exception if the cmd file does not exist.
    int_timeout: If we're interrupted, how long (in seconds) should we give the
      invoked process to clean up before we send a SIGTERM.
    kill_timeout: If we're interrupted, how long (in seconds) should we give the
      invoked process to shutdown from a SIGTERM before we SIGKILL it.
    log_output: Log the command and its output automatically.
    capture_output: Set |stdout| and |stderr| to True.
    quiet: Set |print_cmd| to False, and |capture_output| to True.
    mute_output: Mute subprocess printing to parent stdout/stderr. Defaults to
      None, which bases muting on |debug_level|.
    encoding: Encoding for stdin/stdout/stderr, otherwise bytes are used.  Most
      users want 'utf-8' here for string data.
    errors: How to handle errors when |encoding| is used.  Defaults to 'strict',
      but 'ignore' and 'replace' are common settings.
    dryrun: Only log the command,and return a stub result.

  Returns:
    A CommandResult object.

  Raises:
    RunCommandError: Raised on error.
  """
  # Handle backwards compatible settings.
  if 'log_stdout_to_file' in kwargs:
    logging.warning('run: log_stdout_to_file=X is now stdout=X')
    log_stdout_to_file = kwargs.pop('log_stdout_to_file')
    if log_stdout_to_file is not None:
      stdout = log_stdout_to_file
  stdout_file_mode = 'w+b'
  if 'append_to_file' in kwargs:
    # TODO(vapier): Enable this warning once chromite & users migrate.
    # logging.warning('run: append_to_file is now part of stdout')
    if kwargs.pop('append_to_file'):
      stdout_file_mode = 'a+b'
  assert not kwargs, 'Unknown arguments to run: %s' % (list(kwargs),)

  if quiet:
    print_cmd = False
    capture_output = True

  if capture_output:
    # TODO(vapier): Enable this once we migrate all the legacy arguments above.
    # if stdout is not None or stderr is not None:
    #   raise ValueError('capture_output may not be used with stdout & stderr')
    # TODO(vapier): Drop this specialization once we're Python 3-only as we can
    # pass this argument down to Popen directly.
    if stdout is None:
      stdout = True
    if stderr is None:
      stderr = True

  if encoding is not None and errors is None:
    errors = 'strict'

  # Set default for variables.
  popen_stdout = None
  popen_stderr = None
  stdin = None
  cmd_result = CommandResult()

  # Force the timeout to float; in the process, if it's not convertible,
  # a self-explanatory exception will be thrown.
  kill_timeout = float(kill_timeout)

  def _get_tempfile():
    try:
      return UnbufferedTemporaryFile()
    except EnvironmentError as e:
      if e.errno != errno.ENOENT:
        raise
      # This can occur if we were pointed at a specific location for our
      # TMP, but that location has since been deleted.  Suppress that issue
      # in this particular case since our usage gurantees deletion,
      # and since this is primarily triggered during hard cgroups shutdown.
      return UnbufferedTemporaryFile(dir='/tmp')

  # Modify defaults based on parameters.
  # Note that tempfiles must be unbuffered else attempts to read
  # what a separate process did to that file can result in a bad
  # view of the file.
  log_stdout_to_file = False
  if isinstance(stdout, six.string_types):
    popen_stdout = open(stdout, stdout_file_mode)
    log_stdout_to_file = True
  elif hasattr(stdout, 'fileno'):
    popen_stdout = stdout
    log_stdout_to_file = True
  elif isinstance(stdout, bool):
    # This check must come before isinstance(int) because bool subclasses int.
    if stdout:
      popen_stdout = _get_tempfile()
  elif isinstance(stdout, int):
    popen_stdout = stdout
  elif mute_output or log_output:
    popen_stdout = _get_tempfile()

  log_stderr_to_file = False
  if hasattr(stderr, 'fileno'):
    popen_stderr = stderr
    log_stderr_to_file = True
  elif isinstance(stderr, bool):
    # This check must come before isinstance(int) because bool subclasses int.
    if stderr:
      popen_stderr = _get_tempfile()
  elif isinstance(stderr, int):
    popen_stderr = stderr
  elif mute_output or log_output:
    popen_stderr = _get_tempfile()

  # If subprocesses have direct access to stdout or stderr, they can bypass
  # our buffers, so we need to flush to ensure that output is not interleaved.
  if popen_stdout is None or popen_stderr is None:
    sys.stdout.flush()
    sys.stderr.flush()

  # If input is a string, we'll create a pipe and send it through that.
  # Otherwise we assume it's a file object that can be read from directly.
  if isinstance(input, (six.string_types, six.binary_type)):
    stdin = subprocess.PIPE
    # Allow people to always pass in bytes or strings regardless of encoding.
    # Our Popen usage takes care of converting everything to bytes first.
    #
    # Linter can't see that we're using |input| as a var, not a builtin.
    # pylint: disable=input-builtin
    if encoding and isinstance(input, six.text_type):
      input = input.encode(encoding, errors)
    elif not encoding and isinstance(input, six.text_type):
      input = input.encode('utf-8')
  elif input is not None:
    stdin = input
    input = None

  # Sanity check the command.  This helps when RunCommand is deep in the call
  # chain, but the command itself was constructed along the way.
  if isinstance(cmd, (six.string_types, six.binary_type)):
    if not shell:
      raise ValueError('Cannot run a string command without a shell')
    cmd = ['/bin/bash', '-c', cmd]
    shell = False
  elif shell:
    raise ValueError('Cannot run an array command with a shell')
  elif not cmd:
    raise ValueError('Missing command to run')
  elif not isinstance(cmd, (list, tuple)):
    raise TypeError('cmd must be list or tuple, not %s: %r' %
                    (type(cmd), repr(cmd)))
  elif not all(isinstance(x, (six.binary_type, six.string_types)) for x in cmd):
    raise TypeError('All command elements must be bytes/strings: %r' % (cmd,))

  # If we are using enter_chroot we need to use enterchroot pass env through
  # to the final command.
  env = env.copy() if env is not None else os.environ.copy()
  # Looking at localized error messages may be unexpectedly dangerous, so we
  # set LC_MESSAGES=C to make sure the output of commands is safe to inspect.
  env['LC_MESSAGES'] = 'C'
  env.update(extra_env if extra_env else {})

  if enter_chroot and not IsInsideChroot():
    wrapper = ['cros_sdk']
    if cwd:
      # If the current working directory is set, try to find cros_sdk relative
      # to cwd. Generally cwd will be the buildroot therefore we want to use
      # {cwd}/chromite/bin/cros_sdk. For more info PTAL at crbug.com/432620
      path = os.path.join(cwd, constants.CHROMITE_BIN_SUBDIR, 'cros_sdk')
      if os.path.exists(path):
        wrapper = [path]

    if chroot_args:
      wrapper += chroot_args

    if extra_env:
      wrapper.extend('%s=%s' % (k, v) for k, v in list(extra_env.items()))

    cmd = wrapper + ['--'] + cmd

  for var in constants.ENV_PASSTHRU:
    if var not in env and var in os.environ:
      env[var] = os.environ[var]

  # Print out the command before running.
  if dryrun or print_cmd or log_output:
    log = ''
    if dryrun:
      log += '(dryrun) '
    log += 'run: %s' % (CmdToStr(cmd),)
    if cwd:
      log += ' in %s' % (cwd,)
    logging.log(debug_level, '%s', log)

  cmd_result.args = cmd

  # We want to still something in dryrun mode so we process all the options
  # and return appropriate values (e.g. output with correct encoding).
  popen_cmd = ['true'] if dryrun else cmd

  proc = None
  # Verify that the signals modules is actually usable, and won't segfault
  # upon invocation of getsignal.  See signals.SignalModuleUsable for the
  # details and upstream python bug.
  use_signals = signals.SignalModuleUsable()
  try:
    proc = _Popen(popen_cmd, cwd=cwd, stdin=stdin, stdout=popen_stdout,
                  stderr=popen_stderr, shell=False, env=env,
                  close_fds=True)

    if use_signals:
      if ignore_sigint:
        old_sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)
      else:
        old_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT,
                      functools.partial(_KillChildProcess, proc, int_timeout,
                                        kill_timeout, cmd, old_sigint))

      old_sigterm = signal.getsignal(signal.SIGTERM)
      signal.signal(signal.SIGTERM,
                    functools.partial(_KillChildProcess, proc, int_timeout,
                                      kill_timeout, cmd, old_sigterm))

    try:
      (cmd_result.stdout, cmd_result.stderr) = proc.communicate(input)
    finally:
      if use_signals:
        signal.signal(signal.SIGINT, old_sigint)
        signal.signal(signal.SIGTERM, old_sigterm)

      if (popen_stdout and not isinstance(popen_stdout, int) and
          not log_stdout_to_file):
        popen_stdout.seek(0)
        cmd_result.stdout = popen_stdout.read()
        popen_stdout.close()
      elif log_stdout_to_file:
        popen_stdout.close()

      if (popen_stderr and not isinstance(popen_stderr, int) and
          not log_stderr_to_file):
        popen_stderr.seek(0)
        cmd_result.stderr = popen_stderr.read()
        popen_stderr.close()

    cmd_result.returncode = proc.returncode

    # The try/finally block is a bit hairy.  We normally want the logged
    # output to be what gets passed back up.  But if there's a decode error,
    # we don't want it to break logging entirely.  If the output had a lot of
    # newlines, always logging it as bytes wouldn't be human readable.
    try:
      if encoding:
        if cmd_result.stdout is not None:
          cmd_result.stdout = cmd_result.stdout.decode(encoding, errors)
        if cmd_result.stderr is not None:
          cmd_result.stderr = cmd_result.stderr.decode(encoding, errors)
    finally:
      if log_output:
        if cmd_result.stdout:
          logging.log(debug_level, '(stdout):\n%s', cmd_result.stdout)
        if cmd_result.stderr:
          logging.log(debug_level, '(stderr):\n%s', cmd_result.stderr)

    if check and proc.returncode:
      msg = 'cmd=%s' % cmd
      if cwd:
        msg += ', cwd=%s' % cwd
      if extra_env:
        msg += ', extra env=%s' % extra_env
      raise RunCommandError(msg, cmd_result)
  except OSError as e:
    estr = str(e)
    if e.errno == errno.EACCES:
      estr += '; does the program need `chmod a+x`?'
    raise RunCommandError(estr, CommandResult(args=cmd), exception=e)
  finally:
    if proc is not None:
      # Ensure the process is dead.
      _KillChildProcess(proc, int_timeout, kill_timeout, cmd, None, None, None)

  # We might capture stdout/stderr for internal reasons (like logging), but we
  # don't want to let it leak back out to the callers.  They only get output if
  # they explicitly requested it.
  if stdout is None:
    cmd_result.stdout = None
  if stderr is None:
    cmd_result.stderr = None

  return cmd_result

class CalledProcessError(subprocess.CalledProcessError):
  """Error caught in run() function.

  This is akin to subprocess.CalledProcessError.  We do not support |output|,
  only |stdout|.

  Attributes:
    returncode: The exit code of the process.
    cmd: The command that triggered this exception.
    msg: Short explanation of the error.
    exception: The underlying Exception if available.
  """

  def __init__(self, returncode, cmd, stdout=None, stderr=None, msg=None,
               exception=None):
    if exception is not None and not isinstance(exception, Exception):
      raise TypeError('exception must be an exception instance; got %r'
                      % (exception,))

    super(CalledProcessError, self).__init__(returncode, cmd, stdout)
    # The parent class will set |output|, so delete it.
    del self.output
    # TODO(vapier): When we're Python 3-only, delete this assignment as the
    # parent handles it for us.
    self.stdout = stdout
    # TODO(vapier): When we're Python 3-only, move stderr to the init above.
    self.stderr = stderr
    self.msg = msg
    self.exception = exception

  @property
  def cmdstr(self):
    """Return self.cmd as a well shell-quoted string useful for log messages."""
    if self.cmd is None:
      return ''
    else:
      return CmdToStr(self.cmd)

  def Stringify(self, stdout=True, stderr=True):
    """Custom method for controlling what is included in stringifying this.

    Args:
      stdout: Whether to include captured stdout in the return value.
      stderr: Whether to include captured stderr in the return value.

    Returns:
      A summary string for this result.
    """
    items = [
        'return code: %s; command: %s' % (
            self.returncode, self.cmdstr),
    ]
    if stderr and self.stderr:
      stderr = self.stderr
      if isinstance(stderr, six.binary_type):
        stderr = stderr.decode('utf-8', 'replace')
      items.append(stderr)
    if stdout and self.stdout:
      stdout = self.stdout
      if isinstance(stdout, six.binary_type):
        stdout = stdout.decode('utf-8', 'replace')
      items.append(stdout)
    if self.msg:
      msg = self.msg
      if isinstance(msg, six.binary_type):
        msg = msg.decode('utf-8', 'replace')
      items.append(msg)
    return '\n'.join(items)

  def __str__(self):
    if sys.version_info.major < 3:
      # __str__ needs to return ascii, thus force a conversion to be safe.
      return self.Stringify().encode('ascii', 'xmlcharrefreplace')
    else:
      return self.Stringify()

  def __eq__(self, other):
    return (isinstance(other, type(self)) and
            self.returncode == other.returncode and
            self.cmd == other.cmd and
            self.stdout == other.stdout and
            self.stderr == other.stderr and
            self.msg == other.msg and
            self.exception == other.exception)

  def __ne__(self, other):
    return not self.__eq__(other)

  # TODO(crbug.com/1006587): Migrate users to CompletedProcess and drop this.
class RunCommandError(CalledProcessError):
  """Error caught in run() method.

  Attributes:
    args: Tuple of the attributes below.
    msg: Short explanation of the error.
    result: The CommandResult that triggered this error, if available.
    exception: The underlying Exception if available.
  """

  def __init__(self, msg, result=None, exception=None):
    # This makes mocking tests easier.
    if result is None:
      result = CommandResult()
    elif not isinstance(result, CommandResult):
      raise TypeError('result must be a CommandResult instance; got %r'
                      % (result,))

    self.args = (msg, result, exception)
    self.result = result
    super(RunCommandError, self).__init__(
        returncode=result.returncode, cmd=result.args, stdout=result.stdout,
        stderr=result.stderr, msg=msg, exception=exception)