#!/usr/bin/python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
wg-tool
  Tool to help manage wireguard configs for server and users.
  Guarantee that server and user config kept in sync.
  Handles creating any keys.
  See --help for options and README for details.
gc 20221022
"""
# pylint: disable=C0103
from lib import WgTool

def main():
    """
    Top level entry for wg-tool.
    managers wireguard server wg0.conf as well as users .conf and R codes
    """
    wgtool = WgTool()
    if wgtool.okay:
        wgtool.doit()

# -----------------------------------------------------
if __name__ == '__main__':
    main()
# -------------------- All Done ------------------------
