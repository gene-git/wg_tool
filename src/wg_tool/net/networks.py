# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
Collection of networks
Deals with sub/supersets
"""

from wg_tool.utils import Msg
from wg_tool.utils.debug import pprint

from .network_group import NetGroup
from .network import NetWork


class NetWorks:
    """
    Collection of NetWorks for a VPN.
    Handles overlaps across them.
    If a group is added, the group is added to the
    network which holds that subnet only
    e.g. if networks are 10.0.0.0/24 and fc00/64 then both get a group
    If relying on both ipv4 and ipv6 then add group subnet to both.
    """
    def __init__(self):
        self.okay: bool = True
        self.nets: dict[str, NetGroup] = {}

    def show_list(self):
        """
        Overview of networks
        """
        for (_cidr, netg) in self.nets.items():
            netg.show_list()

    def addr_to_wg_addr(self, addr: str) -> str:
        """
        Return the "wireguard" address from cidr.
        This adds network prefix (taken from its NetWork) to the address string.
        Addresss may have "one" IP prefix /32 (/128 for ipv6)
        e.g. 10.0.0.22/32 -> 10.0.0.22/24
        """
        wg_addr: str = ''
        network = self.ip_to_network(addr)
        if not network:
            return wg_addr

        wg_addr = network.addr_to_wg_addr(addr)
        return wg_addr

    def has_ip_group(self, name: str) -> bool:
        """
        Return true if group exists
        """
        for (_cidr, netg) in self.nets.items():
            if not netg.has_ip_group(name):
                return False
        return True

    def add_ip_group(self, group: str, subnets: list[str]) -> bool:
        """
        Add group/subet to which network subnet is part of

        Group must provide one subnet for each netowrk in this vpn.
        e.g. if we have 10.77.77.0/24 and fc00:77.77::/64 then
        group must provide list of 2 subnets each with 4 IPs;
            (10.77.77.28/30, fc00:77:77::28/126)
            ::28/126 = ::28 - ::2b
        """
        if not subnets:
            return True

        num_nets = len(self.nets)
        num_subnets = len(subnets)

        if num_subnets != num_nets:
            Msg.err(f'Group must provide subnet for each vpn net : {group} \n')
            return False

        if not group:
            Msg.err(f'Missing group name for subnet(s) {subnets}\n')
            return False

        for net in subnets:
            netgroup = self.ip_to_netgroup(net)
            if not netgroup:
                Msg.err(f'Group {group}: {net} not part of this vpn\n')
                return False

            if not netgroup.add_ip_group(group, net):
                return False
        return True

    def _mark_address_taken(self, cidr: str) -> bool:
        """
        Each cidr must be in a known network.
        cidr is marked taken in it's network
        Returns True if all ok
        """
        netgroup = self.ip_to_netgroup(cidr)
        if not netgroup:
            Msg.err(f'Error: Address {cidr} is unkown vpn network\n')
            return False

        if not netgroup.mark_addresses_taken(cidr):
            Msg.err(f'Duplicate address: {cidr}\n')
            return False

        return True

    def mark_addresses_taken(self, cidrs: list[str]) -> bool:
        """
        Each cidr must be in a known network.
        cidr is marked taken in it's network
        Returns True if all ok
        """
        if not cidrs:
            return True

        for cidr in cidrs:
            if not self._mark_address_taken(cidr):
                return False
        return True

    def is_address_available(self, cidr: str) -> bool:
        """
        Return True of CIDR is not taken.
        """
        netgroup = self.ip_to_netgroup(cidr)
        if not netgroup:
            Msg.err(f'Error: Address {cidr} is not part of vpn network')
            return False
        return netgroup.is_address_available(cidr)

    def ip_to_network(self, net_str: str) -> NetWork | None:
        """
        Return NetWork net_str belongs to or None.
        """
        netgroup = self.ip_to_netgroup(net_str)
        if netgroup:
            return netgroup.net
        return None

    def ip_to_netgroup(self, net_str: str) -> NetGroup | None:
        """
        Return NetWork net_str belongs to or None.
        """
        for (_cidr, netgroup) in self.nets.items():
            if netgroup.ip_in_net(net_str):
                return netgroup
        return None

    def ip_to_group_name(self, net_str: str) -> str:
        """
        If net_str is part of group return group name
        """
        netgroup = self.ip_to_netgroup(net_str)
        if not netgroup:
            return ''
        group: str = netgroup.ip_to_group(net_str)
        return group

    def ip_is_subnet(self, cidr: str) -> bool:
        """
        Return True if cidr is in any network.
        """
        netgroup = self.ip_to_netgroup(cidr)
        if netgroup:
            return True
        return False

    def find_new_addresses(self, group: str = '') -> list[str]:
        """
        For each netgroup, get a new address.
        If group is provided, get address from group subnet
        and every subnet must have the same group.
        """
        addresses: list[str] = []

        for (_cidr, netgroup) in self.nets.items():
            net = netgroup.find_new_address(group)
            if net:
                addresses.append(str(net))
            else:
                self.okay = False
        return addresses

    def get_net_strs(self) -> list[str]:
        """
        Return the list of network cidr strings
        These are the "super nets" not broken down by any
        group subnets
        """
        net_str_list: list[str] = list(self.nets.keys())
        return net_str_list

    def get_group_subnets(self) -> dict[str, list[str]]:
        """
        Return group subnets
        Returns:
            {group: list[subnet strings]}
        """
        gsubnets: dict[str, list[str]] = {}
        for (_net_str, netgroup) in self.nets.items():
            if netgroup.subnets:
                for (group, subnet) in netgroup.subnets.items():
                    if not gsubnets.get(group):
                        gsubnets[group] = []
                    subnet_str = subnet.net_str
                    gsubnets[group].append(subnet_str)
        return gsubnets

    def add_cidr(self, cidr: str) -> bool:
        """
        Add cidr. We handle the following:
        - new net
        - subset of existing
        - superset of existing
        - same as already have.
        Return
            True if all ok.
        """
        #
        # Check if existing.
        #
        nets = self.nets
        if cidr in nets:
            return True

        #
        # Check if subnet
        #
        netgroup = self.ip_to_netgroup(cidr)
        if netgroup:
            return True

        #
        # Check if supernet
        #
        for (net_str, netgroup) in nets.items():
            # is_supernet = network.expand_net(cidr)
            is_supernet = netgroup.expand_net(cidr)
            if is_supernet:
                # network expanded
                # update dictionary name to new net
                netg = nets.pop(net_str)
                nets[cidr] = netg
                return True
        #
        # Must be new
        #
        netgroup = NetGroup()
        if not netgroup.initialize(cidr):
            return False

        self.nets[cidr] = netgroup
        return True

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)
        for (_cidr, network) in self.nets.items():
            network.pprint()
