# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
'''
User IP tool
 - ip and cidr: string(s)
 - addr ipa and net : are instances of ipaddress class
'''
# pylint: disable=too-many-instance-attributes
import ipaddress
from ipaddress import (IPv4Network, IPv6Network, IPv4Address, IPv6Address)

from .cidr import (ip_to_address, cidr_to_net, address_iptype, address_to_net)
from .cidr import (net_in_net, sort_nets)

class NetInfo:
    '''
    IP Address data for 1 network
    Based on one wireguard server networks
    NB:
        wg server address is in wg format : IP/cidr_prefix
        i.e. it has host bits as well as prefix
        e.g. 10.1.1.1/24 =>  wg server IP is 10.1.1.1 and network is 10.1.1.0/24
    '''
    def __init__(self, wg_address:str):
        """
        Server has 1 ip in this network
        """
        self.okay: bool = True
        self.wg_address: str = wg_address
        self.server_ip: IPv4Address|IPv6Address = None
        self.iptype: str = None
        self.server_net: IPv4Network|IPv6Network = None

        self.net_avail: [IPv4Network|IPv6Network] = []

        #
        # server address and network
        #
        self.server_ip = ip_to_address(wg_address)
        if not self.server_ip:
            print(f'Bad wg address {wg_address}')
            self.okay = False
            return

        self.iptype = address_iptype(self.server_ip)

        self.server_net = cidr_to_net(wg_address)
        if not self.server_net:
            print(f'Error with address {wg_address}')
            self.okay = False

        #
        # net_avail is list of available nets with available IP addresses
        #  - remove server IP
        #  - remove the network and broadcast addresses as well.
        #  - net_avail.hosts() takes care of not including network / broadcast IPs
        #
        self.net_avail = [cidr_to_net(wg_address)]
        server_ip_net = ipaddress.ip_network(self.server_ip)
        network_address = self.server_net.network_address
        broadcast_address = self.server_net.broadcast_address

        self.mark_address_unavail(server_ip_net)
        self.mark_address_unavail(network_address)
        self.mark_address_unavail(broadcast_address)

    def mark_address_unavail(self, address:str|IPv4Network|IPv6Network|IPv4Address|IPv6Address) -> bool:
        """
        Input address
            can be ip/cidr string, or IPv4Network or IPv6Network or IPv4Address or IPv6Address
        If address in ip_avail remove it
           return true if removed else false
        """
        if not address:
            return False

        addr = address_to_net(address)

        changed = False
        avail = []
        for net in self.net_avail:
            if net_in_net(addr, net):
                changed = True
                net_chg = net.address_exclude(addr)
                avail += list(net_chg)
            else:
                avail.append(net)
        if changed:
            self.net_avail = sort_nets(avail)
        return changed

    def find_address(self, prefix_4, prefix_6, mark_unavail:bool=True) -> [IPv4Network|IPv6Network]:
        """
        Find available nets
        Returns
            One available IP Network (with prefix)
        """
        prefix = prefix_4
        if self.iptype == 'ip6':
            prefix = prefix_6

        if prefix <= 0:
            return None

        # find
        ipnet = None
        for net in self.net_avail:
            net_prefix = net.prefixlen
            if prefix >= net_prefix:
                # pull of the first (aka network address)
                ipa = net.network_address
                ipnet = ipaddress.ip_network(ipa)
                break

        # remove found from available
        if ipnet:
            if mark_unavail:
                self.mark_address_unavail(ipnet)
        else:
            print(f'Failed to find available net {self.iptype} / {prefix}')

        return ipnet

    def ip_in_net(self, ip:str):
        ''' return True if ip is in this net '''
        addr = cidr_to_net(ip)
        ipt = address_iptype(addr)
        if ipt != self.iptype:
            return False
        in_net = addr.subnet_of(self.server_net)
        return in_net

    def is_address_available(self, ip:str):
        ''' check if address in net and available '''
        if not ip:
            return False

        avail = True
        addr = cidr_to_net(ip)
        for net in self.net_avail:
            if addr.subnet_of(net):
                avail = False
                break
        return avail
