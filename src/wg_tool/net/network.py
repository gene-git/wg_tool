# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
User IP tool
 - ip and cidr: string(s)
 - addr ipa and net : are instances of ipaddress class
"""
from py_cidr import PyCidr

from wg_tool.utils import Msg
from wg_tool.utils.debug import pprint


class NetWork:
    """
    IP Address details for 1 wireguard network.
    One network address for wireguard gateway networks.

    Note:

    Address can be "wg address" which has host bits set
    or not. Fine either way.

    wg address has format : IP/prefix
    wher IP has host bits set.
    e.g. 10.1.1.1/24 =>
      wg server: IP: 10.1.1.1
        network: 10.1.1.0/24
    """
    def __init__(self):
        """
        Each peer has 1 ip in this network.

        The network can be either IPv4 or IPv6.

        NB wg ip address has cidr prefix and host bits set.
        e.g. x.x.x.21/24
        So we exract ip (x.x.x.21) and net (x.x.x.0/24)
        unavail is ip, network and broadcast - here:
           x.x.x.21
           x.x.x.0
           x.x.x.255

        The list of available network ips is always generated at load
        time by removing all the IPs used by peers (gateways and clients).

        This way we are sure the list is correct. It also means we can
        check there are no duplicate IPs coming from files.

        VpnInfo is created whenever a vpn with unique name is created.
        The data is stored on disk (work-dir/data/gateways/<vpn-name>/Vpn.info

        avail is really list(ip4) | list(ip6) since its one or the other.
        this seems to make being consistent w pep-484 create
        inappropriate contortions.  such as unnecessary checks if ip4/ip6
        when we've already checked via iptype.
        """
        self.okay: bool = True

        # raw input - can have host bits set (e.g. wg server ip)
        self.net_str: str = ''

        self.ip: str = ''
        self.prefix: int = 0
        self.cidr: str = ''

        self.iptype: str = ''
        self.avail: list[str] = []

        # internal convenience
        # self.prefixlen: dict[str, int] = {'ip4': 32, 'ip6': 128}

    def expand_net(self, cidr: str) -> bool:
        """
        WHen cidr is supernet of net, we can use the larger network.
        Returns True if network was expanded because
        cidr is a super net.
        """
        if PyCidr.is_subnet(self.cidr, [cidr]):
            (ip0, _, ip1) = PyCidr.cidr_to_range(self.cidr)

            if not self.unmark_addresses_taken([ip0, ip1]):
                Msg.err(f' exapand_net: Error unmarking addresses [{ip0}, {ip1}]\n')
                return False

            #
            # initialize updates self.avail marking the new IP and  broadcast/network
            # addresses as taken.
            #
            self.initialize(cidr)
            return True
        return False

    def initialize(self, net_str: str) -> bool:
        """
        Take (wiregiard) netwotk string and initialize avail
        - avail = net_str - server-ip - broadacast-address - network-address
        """
        if not net_str:
            Msg.err('NetWork: Missing vpn network')
            self.okay = False
            return False

        self.net_str = net_str

        if not PyCidr.is_valid_cidr(net_str):
            Msg.err(f'Network: Invalid cidr for VPN network {net_str}')
            self.okay = False
            return False

        (self.ip, self.prefix) = PyCidr.cidr_parts(net_str)
        self.iptype = PyCidr.ip_type(net_str)
        self.cidr = PyCidr.clean_cidr(net_str)

        (network_address, _, broadcast_address) = PyCidr.cidr_to_range(self.cidr)

        #
        # avail is list of subnets with available IP addresses
        #  - avail starts as cidr without server IP or broadcast or network address.
        #  - remove network and broadcast addresses
        #
        # We can be called from expand_net - where self.avail may be in use.
        #
        self.avail += [self.cidr]

        ips_taken: list[str] = [self.ip, network_address, broadcast_address]
        self.avail = PyCidr.exclude_cidrs(self.avail, ips_taken)

        return True

    def get_cidr(self) -> str:
        """
        Return the CIDR for this network.
        Since host bits may be set in net_str we
        generate it directly from Network.
        """
        return self.cidr

    def mark_addresses_taken(self, cidrs: list[str]) -> bool:
        """
        Mark every cidr from the list as taken.
        Any cidr that is not in the netwoek is ignored.
        See mark_address_taken().
        """
        if not cidrs:
            return False

        #
        # Limit to cidrs that are are subnet of self.cidr and available where self.cidr
        # is the clean version of self.net_str with host bits set to zero
        #
        mark_taken: list[str] = []
        for cidr in cidrs:
            if not PyCidr.is_valid_cidr(cidr):
                continue

            # avail can be long list so first check the vpn net itself (supernet of avail)
            if PyCidr.is_subnet(cidr, [self.cidr]) and PyCidr.is_subnet(cidr, self.avail):
                mark_taken.append(cidr)

        #
        # Remove the valid ones from self.avail
        #
        self.avail = PyCidr.exclude_cidrs(self.avail, mark_taken)
        return True

    def mark_address_taken(self, address: str) -> bool:
        """
        Input address:
            Gatewway should mark address only with prefix 32 or 128.
            e.g. x.x.x.10/32

        can be ip or cidr string
        If address in ip_avail remove it
           return true if removed else false
        """
        #
        # Validation
        #
        if not address:
            return False

        if not PyCidr.is_valid_cidr(address):
            return False

        #
        # Check address is in our network.
        #
        ip_in_net = PyCidr.is_subnet(address, [self.cidr])
        if not ip_in_net:
            txt = f'not part of network {self.net_str}'
            Msg.warn(f'Note: cannot mark {address} taken: {txt}\n')
            return False

        #
        # If removing it changed nothing, then was not avail
        # i.e. already used.
        #
        avail = PyCidr.exclude_cidrs(self.avail, [address])
        if avail == self.avail:
            Msg.err(f'Error: IP {address} already used\n')
            return False

        self.avail = avail

        return True

    def get_cidrs_taken(self) -> list[str]:
        """
        Return list of ips in use.
        was: get_net_taken, get_nets_taken
        """
        taken = PyCidr.exclude_cidrs([self.cidr], self.avail)
        return taken

    def unmark_addresses_taken(self, addresses: list[str]) -> bool:
        """
        Free up all addresses in the list.
        Adds the addresses back to available list.
        """
        # confirm all adddresses are in the vpn net before adding then avail list
        newly_avail: list[str] = []
        for cidr in addresses:
            if PyCidr.is_valid_cidr(cidr) and PyCidr.is_subnet(cidr, [self.cidr]):
                newly_avail.append(cidr)

        if not newly_avail:
            return True
        self.avail += newly_avail
        self.avail = PyCidr.compact(self.avail)

        return True

    def unmark_address_taken(self, address: str) -> bool:
        """
        Free up address. Not strictly needed as avail is always
        generated fresh on load.
        """
        if not address:
            return False

        if not PyCidr.is_subnet(address, self.avail):
            txt = f'not subnet of network {self.net_str}'
            Msg.warn(f'Note: cannot mark {address} taken: {txt}\n')
            return False

        self.avail.append(address)
        self.avail = PyCidr.compact(self.avail)

        return True

    def cidr_is_avail(self, cidr: str) -> bool:
        """
        Return True if cidr is not taken
        """
        return PyCidr.is_subnet(cidr, self.avail)

    def is_address_available(self, ip: str) -> bool:
        """
        check if address (or cidr) is in our net and available.
        """
        return PyCidr.is_subnet(ip, self.avail)

    def ip_in_net(self, ip: str) -> bool:
        """
        return True if ip is in our network.
        """
        return PyCidr.is_subnet(ip, [self.cidr])

    def cidr_in_net(self, cidr: str) -> bool:
        """
        return True if ip is in our network.
        """
        return PyCidr.is_subnet(cidr, [self.cidr])

    def net_in_cidr(self, cidr: str):
        """
        Check if our network is subnet of "cidr"
        """
        return PyCidr.is_subnet(self.cidr, [cidr])

    def find_new_address(self, mark_unavail: bool = True) -> str:
        """
        Find an available ip address.

        :returns: One available IP string (with a prefix)
        """
        if not self.avail:
            Msg.err(f' No IP addresses available in net {self.cidr}\n')
            return ''

        (first, _, _) = PyCidr.cidr_to_range(self.avail[0])
        if not first:
            Msg.err(f' Error getting first IP from {self.cidr}\n')
            return ''

        # attach prefix /32 or /128
        first_cidr = PyCidr.clean_cidr(first)

        if mark_unavail:
            self.avail = PyCidr.exclude_cidrs(self.avail, [first_cidr])

        return first_cidr

    def addr_to_wg_addr(self, addr: str) -> str:
        """
        Given an ip address string - generate the "wireguard" ip address
        which has the cidr prefix set to the VPN prefix.
        """
        if not self.cidr_in_net(addr):
            Msg.warn(f'IP {addr} not part of net {self.net_str}\n')

        (ip, _prefix) = PyCidr.cidr_parts(addr)

        net_prefix = self.prefix
        wg_cidr = f'{ip}/{net_prefix}'
        return wg_cidr

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)


def wg_address_to_address(wg_addr: str) -> str:
    """
    Change "wireguard" address to normal address.
    WG address has host bits and prefix for network

    e.g.  10.1.1.22/24 -> 10.1.1.22/32
          fc00:1:1::1/64 -> fc00:1:1::1/128
    """
    (addr, _prefix) = PyCidr.cidr_parts(wg_addr)
    addr = PyCidr.clean_cidr(addr)
    return addr


def wq_addresses_to_addresses(wg_cidrs: list[str]) -> list[str]:
    """
    Given list of wireguard addresses
    Return a list of normal addresses
    """
    cidrs: list[str] = []
    if not wg_cidrs:
        return cidrs

    for wg_cidr in wg_cidrs:
        cidr = wg_address_to_address(wg_cidr)
        cidrs.append(cidr)
    return cidrs
