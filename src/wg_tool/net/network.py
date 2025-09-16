# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
User IP tool
 - ip and cidr: string(s)
 - addr ipa and net : are instances of ipaddress class
"""
import ipaddress

from py_cidr import (Cidr, IPAddress, IPvxNetwork)

from utils import Msg
from utils.debug import pprint


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

        net_avail is really list(ip4) | list(ip6) since its one or the other.
        this seems to make being consistent w pep-484 create
        inappropriate contortions.  such as unnecessary checks if ip4/ip6
        when we've already checked via iptype.
        """
        self.okay: bool = True

        self.net_str: str = ''
        self.net: IPvxNetwork
        self.iptype: str = ''
        self.net_avail: list[IPvxNetwork] = []

        self.prefixlen: dict[str, int] = {'ip4': 32, 'ip6': 128}

    def expand_net(self, net_str: str) -> bool:
        """
        WHen cidr is supernet of net,
        we can use the larget network.
        Returns True if network was expanded becuase
        cidr is a super net.
        """
        if self.net_in_ip(net_str):
            # cidr is supernet of net
            new_net = Cidr.cidr_to_net(net_str)
            if not new_net:
                Msg.err(f'Error with VPN network address {net_str}')
                self.okay = False
                return False
            self.net_str = net_str
            self.net = new_net
            return True

        return False

    def initialize(self, net_str: str) -> bool:
        """
        Map netwotk string to network.
        Initialize net_avail
        """
        if not net_str:
            Msg.err('NetWork: Missing vpn network')
            self.okay = False
            return False

        net = Cidr.cidr_to_net(net_str)
        if net:
            self.net_str = net_str
            self.net = net
        else:
            Msg.err(f'Error with VPN network address {net_str}')
            self.okay = False
            return False

        self.iptype = Cidr.address_iptype(self.net)

        #
        # net_avail is list of nets with available IP addresses
        #  - remove network and broadcast addresses
        #  - net_avail.hosts() takes care of not
        #    using network / broadcast IPs
        #
        self.net_avail = [net]

        #
        # mark network / broadcast unavailable
        #
        if not self.mark_address_taken(net.network_address):
            addr = str(net.network_address)
            Msg.err(f'Error marking VPN network address taken: {addr}')
            return False

        if not self.mark_address_taken(net.broadcast_address):
            addr = str(net.broadcast_address)
            Msg.err(f'Error marking VPN broadcast address taken: {addr}')
            return False

        #
        # Extract any IP from net_str and mark taken
        # net_str may contain host bits (wg works that way)
        # (if was pure network then ip would be same as network_address
        #
        net_ip = Cidr.ip_to_address(net_str)
        if net_ip and net_ip != net.network_address:
            if not self.mark_address_taken(net_ip):
                Msg.err(f'Error marking VPN network address taken: {net_ip}')
                return False
        return True

    def get_cidr(self) -> str:
        """
        Return the CIDR for this network.
        Since host bits may be set in net_str we
        generate it directly from Network.
        """
        if not self.net_str:
            return ''
        cidr = Cidr.net_to_cidr(self.net)
        return cidr

    def mark_address_taken(self, address: IPvxNetwork | IPAddress) -> bool:
        """
        Input address:
            Gatewway should mark address only with prefix 32 or 128.
            e.g. x.x.x.10/32

        can be ip/cidr string, or IPvxNetwork or IPAddress
        If address in ip_avail remove it
           return true if removed else false
        """
        #
        # Validation
        #
        if not address:
            return False

        addr = Cidr.address_to_net(address)
        if not addr or addr is None:
            return False

        #
        # Check address is in our network.
        #
        ip_in_net = addr.subnet_of(self.net)  # type: ignore[arg-type]
        if not ip_in_net:
            txt = f'not part of network {self.net_str}'
            Msg.warn(f'Note: cannot mark {address} taken: {txt}\n')
            return False

        changed = False
        avail: list[IPvxNetwork] = []
        for net in self.net_avail:
            if Cidr.net_is_subnet(addr, net):
                changed = True
                net_chg = net.address_exclude(addr)  # type: ignore[arg-type]
                if net_chg is not None:
                    avail += list(net_chg)
            else:
                avail.append(net)
        if changed:
            self.net_avail = Cidr.sort_nets(avail)
        else:
            Msg.err(f'Error: IP {address} already used\n')
            return False
        return True

    def find_new_address(self, mark_unavail: bool = True
                         ) -> IPvxNetwork | None:
        """
        Find available nets
        Returns
            One available IP Network (with prefix)
        """
        ipnet: IPvxNetwork

        prefix = self.prefixlen[self.iptype]
        if prefix <= 0:
            return None

        # find
        found = False
        for net in self.net_avail:
            net_prefix = net.prefixlen
            if prefix >= net_prefix:
                # pull of the first (aka network) address
                ipa = net.network_address
                ipnet = ipaddress.ip_network(ipa)  # type: ignore[arg-type]
                found = True
                break

        # remove found from available
        if found:
            if mark_unavail:
                self.mark_address_taken(ipnet)
            return ipnet
        Msg.err(f'Failed to find available net {self.iptype} / {prefix}\n')
        return None

    def ip_in_net(self, ip: str) -> bool:
        """
        return True if ip is in our network.
        """
        #
        # check ip is valid
        #
        if not ip:
            return False

        addr = Cidr.cidr_to_net(ip)
        if not addr:
            return False

        # Check is valid and same as our IP type (v4 or v6)
        ipt = Cidr.address_iptype(addr)
        if ipt != self.iptype:
            return False

        # is ip in our network
        ip_in_net = addr.subnet_of(self.net)  # type: ignore[arg-type]
        return ip_in_net

    def net_in_ip(self, cidr: str):
        """
        Check if our network is subnet of "cidr"
        """
        if not cidr:
            return False

        # check is valid and same IP type as us
        addr = Cidr.cidr_to_net(cidr)
        if not addr:
            return False

        # ipt = Cidr.address_iptype(addr)
        ipt = Cidr.cidr_iptype(cidr)
        if ipt != self.iptype:
            return False

        # check if we're a subnet
        is_subnet = self.net.subnet_of(addr)    # type: ignore[arg-type]
        return is_subnet

    def is_address_available(self, ip: str) -> bool:
        """
        check if address (or network) is in our net and available.
        """
        if not ip:
            return False

        avail = True
        addr = Cidr.cidr_to_net(ip)
        if not addr:
            return False

        for net in self.net_avail:
            if addr.subnet_of(net):   # type: ignore[arg-type]
                avail = True
                break
        return avail

    def addr_to_wg_addr(self, ip: str) -> str:
        """
        Given an ip address string - generate the "wireguard"
        which has the cidr prefix set to the VPN prefix.
        """
        if not self.ip_in_net(ip):
            Msg.warn(f'IP {ip} not part of net {self.net_str}\n')

        net_prefix = self.net.prefixlen
        front = ip.split('/', 1)[0] if '/' in ip else ip
        wg_cidr = f'{front}/{net_prefix}'
        return wg_cidr

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)


def wg_address_to_address(wg_cidr: str) -> str:
    """
    Change "wireguard" address to normal address.
    WG address has host bits and prefix for network

    e.g.  10.1.1.22/24 -> 10.1.1.22/32
          fc00:1:1::1/64 -> fc00:1:1::1/128
    """
    net_str: str = ''
    addr = Cidr.ip_to_address(wg_cidr)
    if addr:
        net = Cidr.address_to_net(addr)
        net_str = str(net)
    return net_str


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
