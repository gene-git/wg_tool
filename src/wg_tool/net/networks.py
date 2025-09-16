# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Collection of networks
Deals with sub/supersets
"""

from utils import Msg
from utils.debug import pprint

from .network import NetWork


class NetWorks:
    """
    Collection of NetWork.
    Handles overlaps across them.
    """
    def __init__(self):
        self.okay: bool = True
        self.nets: dict[str, NetWork] = {}

    def addr_to_wg_addr(self, addr: str) -> str:
        """
        Return the "wireguard" address from cidr.
        This adds prefix to an address string.
        Addresss may haver single IP prefix /32 (/128 for ipv6)
        """
        wg_addr: str = ''
        network = self.ip_to_network(addr)
        if not network:
            return wg_addr

        wg_addr = network.addr_to_wg_addr(addr)
        return wg_addr

    def _mark_address_taken(self, cidr: str) -> bool:
        """
        Each cidr must be in a known network.
        cidr is marked taken in it's network
        Returns True if all ok
        """
        network = self.ip_to_network(cidr)
        if not network:
            Msg.err(f'Error: Address {cidr} is unkown vpn network\n')
            return False

        if not network.mark_address_taken(cidr):
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
        network = self.ip_to_network(cidr)
        if not network:
            Msg.err(f'Error: Address {cidr} is not part of server network')
            return False

        if network.is_address_available(cidr):
            return True
        return False

    def ip_to_network(self, net_str: str) -> NetWork | None:
        """
        Return NetWork net_str belongs to or None.
        """
        for (_cidr, network) in self.nets.items():
            if network.ip_in_net(net_str):
                return network
        return None

    def ip_is_subnet(self, cidr: str) -> bool:
        """
        Return True if cidr is in any network.
        """
        for (_cidr, network) in self.nets.items():
            if network.ip_in_net(cidr):
                return True
        return False

    def find_new_addresses(self) -> list[str]:
        """
        For each network (NetWork)
        Get a new address and return them as a list
        """
        addresses: list[str] = []
        for (_cidr, network) in self.nets.items():
            net = network.find_new_address()
            if net:
                addresses.append(str(net))
            else:
                self.okay = False
        return addresses

    def get_net_strs(self) -> list[str]:
        """
        Return the list of network cidr strings
        """
        net_str_list: list[str] = list(self.nets.keys())
        return net_str_list

    def add_cidr(self, cidr: str) -> bool:
        """
        Add cidr. Handle
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
        for (_net_str, network) in nets.items():
            is_subnet = network.ip_in_net(cidr)
            if is_subnet:
                return True

        #
        # Check if supernet
        #
        for (_net_str, network) in nets.items():
            is_supernet = network.expand_net(cidr)
            if is_supernet:
                # network expanded - we're done
                return True
        #
        # Must be new
        #
        network = NetWork()
        if not network.initialize(cidr):
            return False

        self.nets[cidr] = network
        return True

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)
        for (_cidr, network) in self.nets.items():
            network.pprint()
