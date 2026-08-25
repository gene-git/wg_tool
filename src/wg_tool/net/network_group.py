# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
VPN Network divided into subnet groups
Required when one or more subnets are treated differently.
e.g. group of administrators.
All subnets are subnets of the main VPN network.
"""
from py_cidr import PyCidr

from wg_tool.utils import Msg
from wg_tool.utils.debug import pprint

from .network import NetWork


class NetGroup:
    """
    A network with 1 or more subnets (NetWork).
    IPs can be drawn from any of the subnets.
    The primary network (net) has each subnet marked as taken,
    so that IPs drawn from "net" exclude any IPs associated with the subnets.

    IP request with a group name is drawn that group
    subnet, otherwise it is drawn from the named group.
    """
    def __init__(self):
        self.okay: bool = True

        # todo: rename self.net -> self.vpn_net
        self.net: NetWork = NetWork()
        self.initialized: bool = False

        #
        # a group is a named subnet (NetWork)
        # which is a subnet of the primary vpn network
        # (self.net/self.vpn_net)
        #
        self.subnets: dict[str, NetWork] = {}

    def show_list(self):
        """
        Show vpn nets and group/subnets
        """
        Msg.msg(f'    Network {self.net.net_str}\n', fg='208')
        for (group, net) in self.subnets.items():
            Msg.msg(f'      IP-group {group:12s} : {net.net_str}\n')

    def initialize(self, cidr: str) -> bool:
        """
        Initialize the network from cidr
        """
        if not self.net.initialize(cidr):
            return False
        self.initialized = True
        return True

    def has_ip_group(self, name: str) -> bool:
        """
        Return true if group exists
        """
        if name in self.subnets:
            return True
        return False

    def add_ip_group(self, name: str, cidr: str) -> bool:
        """
        Add group
        - check cidr is available
        """
        if not self.initialized:
            Msg.err(f'NetGroup not initialized cannot add group {name} {cidr}\n')
            return False

        #
        # cidr must be subnet of the vpn (super) net
        #
        vpn_cidr = self.net.cidr
        if not PyCidr.is_subnet(cidr, [vpn_cidr]):
            Msg.err(f'NetGroup {name} {cidr} is not subnet of vpn {vpn_cidr}\n')
            return False

        #
        # Initialize network
        # - NetwWork initialize removes ip, network addr and broadcast addr from subnet
        # - we also need to sync the avail nets in vpn itself and this subnet
        #   e.g. vpn server IP, network and broadcast addresses must be removed
        #   if they are part of this subnet.
        #   e.g. vpn = 10.0.0.0/22 and admin_subnet = 10.0.0.0/24
        #   then ab initio admin subnet must exclude 10.0.0.0 (but 10.0.0.255 is allowed).
        #   However by default initialize will remove 10.0.0.0 and 10.0.0.255.
        #   Which is fine if unnecessary.
        #   In addition if the vpn has used 10.0.0.50 it too must be removed from admin
        #   subnet.
        #
        subnet = NetWork()
        if not subnet.initialize(cidr):
            return False

        #
        # 'already_taken' list are the vpn ip, network and broadcast addresses
        # as well any IP already take from this subnet.
        #
        already_taken: list[str] = []
        vpn_taken = self.net.get_cidrs_taken()
        for taken in vpn_taken:
            if PyCidr.is_subnet(taken, [cidr]):
                already_taken.append(taken)
        #
        # Remove from subnet
        #
        if already_taken:
            if not subnet.mark_addresses_taken(already_taken):
                Msg.err(f' Error removing IPs from grop {name} : {cidr}\n')
                return False
        #
        # Mark the entire group subnet as not avail from the vpn's own
        # avail list.
        #
        self.net.avail = PyCidr.exclude_cidrs(self.net.avail, [cidr])

        self.subnets[name] = subnet
        return True

    def mark_addresses_taken(self, cidr: str) -> bool:
        """
        Mark cidr as taken
        """
        if not cidr:
            return True

        group = self.ip_to_group(cidr)
        if group:
            net = self.subnets[group]
        else:
            net = self.net
        return net.mark_address_taken(cidr)

    def ip_in_net(self, net_str: str) -> bool:
        """
        Return True if net_str is in Network
        """
        return self.net.ip_in_net(net_str)

    def ip_to_group(self, cidr: str) -> str:
        """
        If cidr part of any groups return the group
        """
        for (name, net) in self.subnets.items():
            if net.ip_in_net(cidr):
                return name
        return ''

    def is_address_available(self, cidr: str) -> bool:
        """
        Return true if address is available
        False if not part of the net
        """
        if not self.ip_in_net(cidr):
            return False

        # check groups first
        group = self.ip_to_group(cidr)
        if group:
            net = self.subnets[group]
        else:
            net = self.net

        available = net.cidr_is_avail(cidr)
        return available

    def find_new_address(self, group: str = '') -> str:
        """
        Return new address.
        If group specified then group must be available.
        """
        if not group:
            net = self.net

        elif group in self.subnets:
            net = self.subnets[group]

        else:
            Msg.err(f'Unkown group {group}\n')
            return ''

        addr = net.find_new_address()
        if addr:
            return addr
        return ''

    def expand_net(self, cidr: str) -> bool:
        """
        Check if cidr is a super net
        """
        return self.net.expand_net(cidr)

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)
        self.net.pprint()
        for (_name, net) in self.subnets.items():
            net.pprint()
