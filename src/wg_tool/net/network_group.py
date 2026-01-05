# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
Network diviced into subnet groups
Needed when one or more subnets are treated differently.
e.g. group of administrators.
"""
import ipaddress
from wg_tool.utils import Msg
from wg_tool.utils.debug import pprint

from .network import NetWork


class NetGroup:
    """
    A network with subnets. IPs can be drawn from
    any of the subnets. The primary network (net)
    has each subnet marked as taken, so that IPs drawn from
    "net" exclude any IPs associated with the subnets.

    IP request with a group name is drawn that group
    subnet, otherwise it is drawn from the named group.
    """
    def __init__(self):
        self.okay: bool = True
        self.net: NetWork = NetWork()
        self.initialized: bool = False

        # Group is subnet and a name.
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
        # Initialize network
        # - remove network/broadcast ips (wrt net)
        #
        subnet = NetWork()
        if not subnet.initialize(cidr):
            return False
        vpn_net = self.net.net
        skips = (
                ipaddress.ip_network(vpn_net.network_address),
                ipaddress.ip_network(vpn_net.broadcast_address)
                )
        for skip in skips:
            if subnet.net_is_avail(skip):
                subnet.mark_address_taken(skip)

        #
        # check that the available ips of subnet
        # Are available from vpn net
        # NB - must do this after removing network/broadcast addresses above
        # - Mark each not available
        #
        for net in subnet.net_avail:
            if not self.net.net_is_avail(net):
                Msg.err(f'NetGroup: network not available: {name} {cidr}\n')
                Msg.err(f'  Cannot use {str(net)}\n')
                return False
            if not self.net.mark_address_taken(net):
                return False

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
            return str(addr)
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
