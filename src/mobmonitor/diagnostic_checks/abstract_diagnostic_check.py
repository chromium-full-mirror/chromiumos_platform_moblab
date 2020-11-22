# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


class AbstractDiagnosticCheck:
    """
    Defines the interface for a diagnostic check
    Any new diagnostic checks should override the properties
    and methods defined here
    """

    # High level category for this check (network, disk etc)
    # Diagnostics are grouped by category in the UI
    category = "abstract category"

    # Name for this diagnostic
    name = "abstract name"

    # A short description of what the diagnostic does
    description = "abstract description"

    def run(self):
        """
        Override with the code that actually gathers and processes diagnostic
        information.

        Return:
            free form text containing the results of the diagnostic
        Raise:
            DiagnosticError with a helpful message if any error occurs
        """
        pass
