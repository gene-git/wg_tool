#!/usr/bin/python
"""
wg-tool
  Tool to help manage wireguard configs for server and users. 
  Guarantee that server and user config kept in sync.
  Handles creating any keys.
  See --help for options and README for details.
gc 20221022
"""
# pylint: disable=C0103
# import pdb
from lib import WgTool

def main():
    """
    Top level entry for wg-tool.
    managers wireguard server wg0.conf as well as users .conf and R codes
    """
    # pdb.set_trace()
    wgtool = WgTool()
    if wgtool.okay:
        wgtool.doit()

# -----------------------------------------------------
if __name__ == '__main__':
    main()
# -------------------- All Done ------------------------
