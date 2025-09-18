#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
# PYTHON_ARGCOMPLETE_OK

"""
wg-tool
  Manages wireguard configuration.
  Guarantees server side and user configs are
  always in sync (public keys etc).
  See --help for options and README for details.
"""
# pylint: disable=invalid-name
from app import Tool


def main():
    """
    Top level entry for wg-tool.
    managers wireguard server wg0.conf as well as users .conf and R codes
    """
    tool = Tool()
    if tool.okay:
        tool.doit()


# -----------------------------------------------------
if __name__ == '__main__':
    main()
