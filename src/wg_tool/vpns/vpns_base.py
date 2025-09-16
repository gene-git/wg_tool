# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Handles 1 "vpn".
"""
# pylint: disable=too-few-public-methods
from config import Opts
from vpn import Vpn


class VpnsBase:
    """
    Class for all VPNCs.

    List of vpns where each vpn contains:
    - vpninfo
    - peers (gateways & clients)
    """
    def __init__(self, opts: Opts):

        self.opts: Opts = opts
        self.vpn: dict[str, Vpn] = {}
