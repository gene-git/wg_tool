# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Wireguard uses these configs
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes

from config import Opts
from vpninfo import VpnInfo
from net import NetsShared

from .acct import Acct


class WgConfigBase:
    """
    Each profile has it's own wireguard config has 2 kinds of sections
     - [Interface]
     - [Peer]
    There is one interface and one or more peer sections.
    See wireguard docs and man pages for wg and wg-quick

    This class is used to generate them.
    """
    def __init__(self, opts: Opts, vpninfo: VpnInfo, accts: dict[str, Acct]):

        self.opts: Opts = opts
        self.vpninfo: VpnInfo = vpninfo
        self.accts: dict[str, Acct] = accts

        #
        # dns via: vpninfo, gateways and each profile.
        # here we gather vpnfino and all gateways.
        #
        self.dns: list[str] = []
        self.dns_search: list[str] = []

        #
        # helpers used in constructing the configs
        # All names are for active accounts/profiles only.
        # We ignore inactives in all wireguard config output.
        # - acct_names = list of all accts
        # - prof_names = profile names {account: [profile list]}
        # - gw_prof_names = list of gateways {account: [profile list]}
        # - cl_prof_names = list of clients {account: [profile list]}
        # - cl_allowed = nets via clients - re-shared by gateways
        # - peer_to_peer_names = list of peers requesting ability
        # - peers_by_net = list of peer idents for each shared network.
        #
        self.acct_names: list[str] = []
        self.prof_names: dict[str, list[str]] = {}

        self.gw_prof_names: dict[str, list[str]] = {}
        self.cl_prof_names: dict[str, list[str]] = {}

        self.nets_shared: NetsShared = NetsShared()

        self.gw_nets_offered: list[str] = []
        self.cl_nets_offered: list[str] = []

        # list of ids of any gateways with alternate endpoint
        self.gw_alternates: list[str] = []
