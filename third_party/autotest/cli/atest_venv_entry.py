#!/usr/bin/python2 -u
import os
import sys

import common

_AUTOTEST_ROOT = os.path.realpath(os.path.join(__file__, '..', '..'))
_CHROMIUMOS_ROOT = os.path.abspath(
    os.path.join(_AUTOTEST_ROOT, '..', '..', '..', '..'))

from autotest_lib.cli import atest

sys.exit(atest.main())
