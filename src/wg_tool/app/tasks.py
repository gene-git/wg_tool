# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Do all tasks
"""

from utils import Msg
from utils import set_restrictive_file_perms
from data import get_top_dir
from data import get_top_wg_dir
from vpns import Vpns

from .cleanup import cleanup


def do_tasks(vpns: Vpns) -> bool:
    """
    Run the tool.
      - NB The config writers only write if changed
      - wg config outputs are always updated.
      In general operations are applied to:
        - all users/configs : if 'all' or none specified
        - users/configs specified on command line if any listed
    """
    opts = vpns.opts

    if opts.refresh:
        vpns.refresh()

    #
    # Import
    #
    if opts.import_configs:
        vpn_name = opts.import_configs
        if not vpns.import_configs(vpn_name):
            return False

    if opts.modify:
        # handle:
        #   (not-)active, (not-)hidden, edit, copy
        #   merge, rename, new
        #
        if not vpns.modify():
            return False
    #
    # Roll keys
    #  - server -> feed new pub key to all users
    #
    if opts.roll_keys:
        if not vpns.new_key_pairs():
            return False

    #
    # List all peers
    #
    if opts.list:
        vpns.show_list()

    #
    # show rpt
    #
    if opts.show_rpt or opts.run_show_rpt:
        vpns.show_rpt()

    #
    # save config data
    #
    vpns.write()

    #
    # save wireguard data
    #
    vpns.write_wireguard()

    #
    # Extra caution to ensure permissions are user/root only
    #
    if opts.file_perms:
        Msg.plainverb(' Refresh restricted file perms\n', level=2)

        # file perms
        topdir = get_top_dir(opts.work_dir)
        set_restrictive_file_perms(topdir)

        topdir = get_top_wg_dir(opts.work_dir)
        set_restrictive_file_perms(topdir)
    #
    # clean up
    #
    cleanup(vpns)
    return True
