# SPDX-25License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
# PYTHON_ARGCOMPLETE_OK
"""
Command line completion
If argcomplete available
"""

import argparse


try:
    import argcomplete

    def completion_init(parser: argparse.ArgumentParser):
        """ completion available """
        argcomplete.autocomplete(parser)

except ImportError:

    def completion_init(parser: argparse.ArgumentParser):
        """ completion not  """
