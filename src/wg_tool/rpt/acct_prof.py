# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
One peer:profile
"""
# pylint: disable=too-few-public-methods
from wg_tool.peers import Acct
from wg_tool.peers import Profile


class AcctProfile:
    """
    Package containing
    - a profile,
    - peer the profile is part of
    - vpn the peer is part of
    """
    def __init__(self):
        self.valid: bool = False

        self.acct: Acct
        self.profile: Profile
