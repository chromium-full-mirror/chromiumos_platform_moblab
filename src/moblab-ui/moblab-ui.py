#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""The Moblab web interface."""

from __future__ import print_function

import cherrypy
import os
import sys
import logging.handlers
import argparse

from chromite.lib import cros_logging as logging

STATICDIR = '/etc/moblab/moblab-ui/static/'

LOGDIR = '/var/log/moblab-ui/'
LOGFILE = 'moblab-ui.log'
LOGFILE_SIZE_BYTES = 1024 * 1024
LOGFILE_COUNT = 10


class MoblabUIRoot(object):
    """The central object supporting the Mob* Monitor web interface."""

    def __init__(self, staticdir=STATICDIR):
        if not os.path.exists(staticdir):
            raise IOError('Static directory does not exist: %s' % staticdir)

        self.staticdir = staticdir

    @cherrypy.expose
    def index(self):
        """Presents a welcome message."""
        raise cherrypy.HTTPRedirect('/static/index.html')


def SetupLogging(logdir):
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s:%(name)s:%(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M',
        filename=os.path.join(logdir, LOGFILE),
        filemode='w')
    rotate = logging.handlers.RotatingFileHandler(
        os.path.join(logdir, LOGFILE),
        maxBytes=LOGFILE_SIZE_BYTES,
        backupCount=LOGFILE_COUNT)
    logging.getLogger().addHandler(rotate)


def ParseArguments(argv):
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        '-p', '--port', type=int, default=6010, help='The Mob* Monitor port.')
    parser.add_argument(
        '-s',
        '--staticdir',
        default=STATICDIR,
        help='Ui static content directory')
    parser.add_argument(
        '--logdir',
        dest='logdir',
        default=LOGDIR,
        help='Moblab ui log file directory.')

    return parser.parse_args(argv)


def _validate_port(check_port):
    port = int(check_port)
    if port <= 0 or port >= 65536:
        raise ValueError('%d is not a valid port' % port)
    return port


def main(argv):
    options = ParseArguments(argv)

    # Configure logger.
    SetupLogging(options.logdir)

    # Configure global cherrypy parameters.
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': _validate_port(options.port)
    })

    mobuiappconfig = {
        '/': {
            'tools.staticdir.root': options.staticdir
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': ''
        },
        '/static/css': {
            'tools.staticdir.dir': 'css'
        },
        '/static/js': {
            'tools.staticdir.dir': 'js'
        }
    }

    # Setup the moblab-ui
    mobui = MoblabUIRoot(staticdir=options.staticdir)

    # Start the Mob* Monitor.
    cherrypy.quickstart(mobui, config=mobuiappconfig)


if __name__ == '__main__':
    main(sys.argv[1:])
