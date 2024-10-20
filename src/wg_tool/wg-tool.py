#!/usr/bin/python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
'''
wg-tool
  Tool to manage wireguard server and users.
  Guarantee server and user config kept in sync (public keys)
  See --help for options and README for details.
gc 20221022
'''
# pylint: disable=invalid-name
from wg import WgTool

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
