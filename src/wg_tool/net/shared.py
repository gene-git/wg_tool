# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Shared networks
"""
import itertools
from py_cidr import Cidr
from py_cidr import IPvxNetwork

from utils import Msg


class NetShared:
    """
    A single shared nwtwork.
    """
    def __init__(self, cidr: str):
        """
        cidr - The network
        peers - list of profile ident.id_str
        """
        self.ok: bool = True

        # network info
        self.cidr: str = cidr

        self.net: IPvxNetwork
        self.subnet_of: list[str] = []
        self.supernet_of: list[str] = []

        net = Cidr.cidr_to_net(cidr)
        if net:
            self.net = net
        else:
            self.ok = False

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
    List of all shared networks.
    """
    def __init__(self):
        self.ok: bool = True
        self.shared: list[NetShared] = []

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
        """
        self._update_subnets()
        # self._update_nets_by_peers()
        # self._update_peers_by_nets()

    def add_wanted_by(self, peer: str, cidrs: list[str]) -> bool:
        """
        Adds cidrs and mark each wanted by peer (id_str)
        """
        for cidr in cidrs:
            self._add_cidr_wanted_by(peer, cidr)
        return True

    def add_offered_by(self, peer: str, cidrs: list[str]) -> bool:
        """
        Adds cidrs and mark each offered by peer (id_str)
        """
        for cidr in cidrs:
            self._add_cidr_offered_by(peer, cidr)
        return True

    def get_common_nets(self, peer1: str, peer2: str) -> list[str]:
        """
        Returns list of common networks which are offered by one
        and wanted by the other (or vice versa).

        Handles subnets.
        e.g. peer1 has x/22 and peer2 has x/24 then common is
             smaller of the 2, which is /24
        """
        nets: list[str] = []
        if not (peer1 and peer2):
            return nets

        #
        # make set of (unique) pairs of shared net from each peer.
        # where with shared from each peer.
        # When shared is same for both peers, add the cidr
        # and thus skip tuple(x, x) where x is same shared net.
        # Each pair is tuple(shared_a, shared_b)
        # Use sort on cidr to ensure (a, b) is treated same as (b, a)
        # and only included once.
        #
        shared_1 = self._shared_wanted_by(peer1)
        shared_2 = self._shared_offered_by(peer2)
        nets = _common_nets(shared_1, shared_2)

        shared_1 = self._shared_wanted_by(peer2)
        shared_2 = self._shared_offered_by(peer1)
        nets += _common_nets(shared_1, shared_2)

        nets = list(set(nets))
        return nets

    def _add_cidr_wanted_by(self, peer: str, cidr: str) -> bool:
        """
        Adds cidr and wanted_by peer (peer = ident.id_str)
        """
        (ok, shared) = self._add_shared_for_cidr(cidr)
        if not ok:
            return False

        shared.add_wanted_by(peer)
        return True

    def _add_cidr_offered_by(self, peer: str, cidr: str) -> bool:
        """
        Adds cidr and offered_by peer (peer = ident.id_str)
        """
        (ok, shared) = self._add_shared_for_cidr(cidr)
        if not ok:
            return False

        shared.add_offered_by(peer)
        return True

    def _add_shared_for_cidr(self, cidr: str) -> tuple[bool, NetShared]:
        """
        Returns NetShared with 'cidr' - creates it if not found
        """
        shared = self._shared_for_cidr(cidr)
        if not shared:
            shared = NetShared(cidr)
            if not shared.ok:
                Msg.err(f'Invalid net {cidr}\n')
                return (False, shared)
            self.shared.append(shared)
        return (True, shared)

    def _update_subnets(self):
        """
        Identify which are subnet of another.
        By subnet_of we exclude the equality case
        """
        for (sh_1, sh_2) in itertools.combinations(self.shared, 2):
            if sh_1.cidr == sh_2.cidr:
                # This is an error and should never happen
                # dont bother repairing this just display error
                self.ok = False
                Msg.err(f'Error: Duplicate cidrs: {sh_1.cidr}\n')
                continue

            if Cidr.net_is_subnet(sh_1.net, sh_2.net):
                sh_1.subnet_of.append(sh_2.cidr)
                sh_2.supernet_of.append(sh_1.cidr)

            elif Cidr.net_is_subnet(sh_2.net, sh_1.net):
                sh_2.subnet_of.append(sh_1.cidr)
                sh_1.supernet_of.append(sh_2.cidr)

    def _shared_for_cidr(self, cidr: str) -> NetShared | None:
        """
        Return net shared which owns "net"
        """
        if not cidr:
            return None

        for shared in self.shared:
            if cidr == shared.cidr:
                return shared
        return None

    def _shared_wanted_by(self, peer: str) -> list[NetShared]:
        """
        Return list of all NetShared wanted by this peer
        """
        shared_all: list[NetShared] = []
        if not peer:
            return shared_all

        for shared in self.shared:
            if peer in shared.wanted_by:
                shared_all.append(shared)
        return shared_all

    def _shared_offered_by(self, peer: str) -> list[NetShared]:
        """
        Return list of all NetShared offered by this peer
        """
        shared_all: list[NetShared] = []
        if not peer:
            return shared_all

        for shared in self.shared:
            if peer in shared.offered_by:
                shared_all.append(shared)
        return shared_all


def _common_nets(shared_1_all: list[NetShared], shared_2_all: list[NetShared]
                 ) -> list[str]:
    """
    Determine the common nets shared by the 2 lists
    For nets to be shared they must be wanted by one and offered by the other.
    """
    nets: list[str] = []
    pairs: set[tuple[NetShared, NetShared]] = set()

    if not (shared_1_all and shared_2_all):
        # should not be possible.
        return nets

    #
    # create ordered set of (unique) pairs
    # with (A, B) with A>B (exclude A==B)
    #
    for (sh_1, sh_2) in itertools.product(shared_1_all, shared_2_all):
        # the same net
        if sh_1.cidr == sh_2.cidr:
            nets.append(sh_1.cidr)
            continue

        # ordered pair (a,b) treated same as (b,a)
        # - order not important
        # if sh_1.net <= sh_2.net:
        if _net_is_less_than_equal(sh_1.net, sh_2.net):
            pairs.add((sh_2, sh_1))
        else:
            pairs.add((sh_1, sh_2))

    # Pull out the common nets from pairs
    # common means: equal or subnet
    nets_set: set[str] = set()
    for (sh_1, sh_2) in pairs:
        if sh_1.cidr == sh_2.cidr:
            nets_set.add(sh_1.cidr)

        elif sh_1.cidr_is_sub(sh_2.cidr):
            nets_set.add(sh_1.cidr)

        elif sh_2.cidr_is_sub(sh_1.cidr):
            nets_set.add(sh_2.cidr)

    nets += list(nets_set)

    return nets


def _net_is_less_than_equal(net1: IPvxNetwork, net2: IPvxNetwork) -> bool:
    """
    Return true if net1 < net2
    Handle mixed ipv4 / ipv6
    by "defining" ipv4 < ipv6
    """
    net1_ip4 = Cidr.is_valid_ip4(net1)
    net2_ip4 = Cidr.is_valid_ip4(net2)

    ip4 = net1_ip4 and net2_ip4
    ip6 = not net1_ip4 and not net2_ip4

    if ip4 or ip6:
        return net1 <= net2         # type: ignore[operator]

    if net1_ip4:
        return True
    return False
