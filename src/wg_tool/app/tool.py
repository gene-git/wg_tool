# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
wg-tool primary class

Tool to administer wireguard vpns.
Each "vpn" has its own suite of peers. Some peers are clients
which connect to a gateway (which listens on a known ip/port)
"""
# pylint: disable=too-few-public-methods

from config import Opts
from utils import Msg
from vpns import Vpns

from .data_migration import do_data_migration
from .tasks import do_tasks


class Tool:
    """
    Class Wireguard Tool
    """
    def __init__(self):
        self.okay: bool = True

        # options
        self.opts = Opts()
        if not self.opts.okay:
            self.okay = False
            return

        if self.opts.verb > 0:
            Msg.verb = self.opts.verb

        #
        # Check if migrating from older config version
        # - migration writes out the new config data
        #
        (need_migrate, done_migrate) = do_data_migration(self.opts)
        if need_migrate and not done_migrate:
            self.okay = False
            return

        if not self.opts.check():
            self.okay = False
            return

        #
        # Load up vpn(s)
        # - each vpn has its own set of peers.
        #
        self.vpns = Vpns(self.opts)

    def doit(self):
        """
        Run the tool.
          - NB The config writers only write if changed
          - wg config outputs are always updated.
          In general operations are applied to:
            - all users/configs : if 'all' or none specified
            - users/configs specified on command line if any listed
        """
        ok = do_tasks(self.vpns)
        if ok:
            Msg.hdr('Completed\n')
        else:
            self.okay = False
            Msg.hdr('Errors encounterd\n')
