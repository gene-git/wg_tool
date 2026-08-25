# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
Shared networks
- networks (other than the vpn net) offered by peers to other peers
  wanting access - offered_by nets and wanted_by_nets.
"""
import itertools
from py_cidr import PyCidr

from wg_tool.utils import Msg


class NetShared:
    """
    A single shared nwtwork.
    """
    def __init__(self, cidr: str):
        """
        cidr - The network
        offered by - list of IDs (profile ident.id_str) offering
        wanted_by  - list of IDs wanting access to this network.
        """
        self.ok: bool = True

        # network info
        self.cidr: str = cidr

        # Are these used - if not lets remove them.
        self.subnet_of: list[str] = []
        self.supernet_of: list[str] = []

        if not PyCidr.is_valid_cidr(cidr):
            Msg.err(f'Invalid network {cidr}\n')
            self.ok = False

        #
        # list of peers (IDs) offering or wanting this cidr subnet
        #
        self.wanted_by: list[str] = []
        self.offered_by: list[str] = []

    def cidr_is_sub(self, cidr: str) -> str:
        """
        Return cidr
            if cidr is subnet of self.cidr
        """
        if cidr == self.cidr or cidr in self.subnet_of:
            return cidr
        return ''

    def add_wanted_by(self, peer: str):
        """
        Add this peer to list
        """
        if peer not in self.wanted_by:
            self.wanted_by.append(peer)

    def add_offered_by(self, peer: str):
        """
        Add this peer to list
        """
        if peer not in self.offered_by:
            self.offered_by.append(peer)


class NetsShared:
    """
    Collection of all the shared networks.
    Which peer(s) wants them and which peer(s) offer them.
    """
    def __init__(self):
        self.ok: bool = True

        # {cidr: [net1, net2, ...]
        self.shared_nets: dict[str, NetShared] = {}

        # {peer: [cidr1, cidr2, ... ]}
        self.offered_by: dict[str, list[str]] = {}
        self.wanted_by: dict[str, list[str]] = {}

        self.nets_by_peers: dict[str, list[str]] = {}
        self.peers_by_nets: dict[str, list[str]] = {}

    def refresh(self):
        """
        Call after all shared are added.
        Ascertain all that are subnets of others
        Update self.nets_by_peers, self.peers_by_net
        Every unique cidr string gets its own instance of NetShared.
        This way we can track if any are sub/super nets of
        others.

        todo: remove this - nothing is using supernet_of/subnet_of in these shared nets
        """
        self._update_subnets()

    def add_wanted_by(self, peer: str, cidrs: list[str]) -> bool:
        """
        Adds cidrs and mark each wanted by the peer (id_str)
        """
        if not peer or not cidrs:
            return False

        if peer not in self.wanted_by:
            self.wanted_by[peer] = list(set(cidrs))
        else:
            self.wanted_by[peer] = list(set(self.wanted_by[peer] + cidrs))

        for cidr in cidrs:
            shared_net = self._get_shared_net(cidr)
            if not shared_net.ok:
                continue
            shared_net.add_wanted_by(peer)

        return True

    def add_offered_by(self, peer: str, cidrs: list[str]) -> bool:
        """
        Adds cidrs and mark each offered by peer (id_str)
        """
        if not peer or not cidrs:
            return False

        if peer not in self.offered_by:
            self.offered_by[peer] = list(set(cidrs))
        else:
            self.offered_by[peer] = list(set(self.offered_by[peer] + cidrs))

        for cidr in cidrs:
            shared_net = self._get_shared_net(cidr)
            if not shared_net.ok:
                continue
            shared_net.add_offered_by(peer)

        return True

    def get_common_nets(self, peer1: str, peer2: str) -> list[str]:
        """
        Returns list of common networks which are offered by one
        and wanted by the other (or vice versa).

        Handles subnets.
        e.g. peer1 has x/22 and peer2 has x/24 then common is
             smaller of the 2, which is /24

        This functionality is provided by PyCidr.cidrs_intersection()
        """
        if not (peer1 and peer2):
            return []

        nets: list[str] = []

        if peer1 in self.offered_by and peer2 in self.wanted_by:
            offered_1 = self.offered_by[peer1]
            wanted_2 = self.wanted_by[peer2]
            nets = PyCidr.cidrs_intersection(offered_1, wanted_2)

        if peer2 in self.offered_by and peer1 in self.wanted_by:
            offered_2 = self.offered_by[peer2]
            wanted_1 = self.wanted_by[peer1]
            nets += PyCidr.cidrs_intersection(offered_2, wanted_1)

        return nets

    def _get_shared_net(self, cidr: str) -> NetShared:
        """
        Returns NetShared with 'cidr' - creates it if not found
        Caller should check shared.ok
        """
        if cidr not in self.shared_nets:
            self.shared_nets[cidr] = NetShared(cidr)

        shared_net = self.shared_nets[cidr]
        return shared_net

    def _update_subnets(self):
        """
        Identify which are subnet of another.
        By subnet_of we exclude the equality case
        i.e. look at all pairs of shared blocks and determina
        if either is subnet of the other.
        """
        all_cidrs = list(self.shared_nets.keys())
        if not all_cidrs or len(all_cidrs) < 2:
            return

        all_cidrs = PyCidr.sort(all_cidrs)

        for (cidr_1, cidr_2) in itertools.combinations(all_cidrs, 2):
            if cidr_1 == cidr_2:
                self.ok = False
                Msg.err(f'Error: Duplicate shared cidrs: {cidr_1}\n')
                continue

            shared_net_1 = self.shared_nets[cidr_1]
            shared_net_2 = self.shared_nets[cidr_2]

            if PyCidr.is_subnet(cidr_1, [cidr_2]):
                shared_net_1.subnet_of.append(cidr_2)
                shared_net_2.supernet_of.append(cidr_1)

            elif PyCidr.is_subnet(cidr_2, [cidr_1]):
                shared_net_2.subnet_of.append(cidr_1)
                shared_net_1.supernet_of.append(cidr_2)
