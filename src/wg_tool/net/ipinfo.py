# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
'''
User IP tool
 - ip and cidr: string(s)
 - addr ipa and net : are instances of ipaddress class
'''
# pylint: disable=too-many-instance-attributes

from .cidr import (cidr_to_net, cidr_iptype)
from .netinfo import NetInfo

from .types import Stringy

class IpInfo:
    '''
    manage user ips
    '''
    # pylint: disable=too-few-public-methods
    def __init__(self, wg_server_addresses):
        #
        # server_ips in wg format which combine IP with cidr prefix
        # Clients get one address from each wg_server network
        #
        self.okay = True
        self.wg_server_addresses = wg_server_addresses
        self.netinfo = {}
        self.prefixlen_4 = 32
        self.prefixlen_6 = 128
        self.allowed_ips = '0.0.0.0/0, ::/0'

        for wg_addr in wg_server_addresses:
            netinfo = NetInfo(wg_addr)
            if netinfo.okay:
                self.netinfo[wg_addr] = netinfo
            else:
                return

    def set_prefixlen(self, prefixlen_4:int, prefixlen_6:int):
        """ store current prefix lens """
        self.prefixlen_4 = prefixlen_4
        self.prefixlen_6 = prefixlen_6

    def find_address(self) -> [str]:
        """
        Returns list of usable address strings for each server network
        """
        addresses = []
        for (_wg_addr, netinfo) in self.netinfo.items():
            net = netinfo.find_address(self.prefixlen_4, self.prefixlen_6)
            if net:
                addresses.append(str(net))
            else:
                self.okay = False
        return addresses

    def is_address_available(self, cidr:str):
        """
        check if address (ip or cidr) is available
        """
        netinfo = self.get_netinfo(cidr)
        if not netinfo:
            print(f'Error: Address {cidr} is not part of server network')
            return False

        if netinfo.is_address_available(cidr):
            return True
        return False

    def mark_addresses_unavail(self, cidrs:[str]):
        """
        Add cidr_str to list of used
        Must be in one of the known nets
        """
        for cidr in cidrs:
            netinfo = self.get_netinfo(cidr)
            if netinfo:
                netinfo.mark_address_unavail(cidr)
            else:
                print(f'Warning: Address {cidr} not in server networks - cannot mark as used')
                print('         Cannot add to list of used IP addresses')

    def get_netinfo(self, cidr:str):
        """
        Return netinfo that cidr belongs to or None
        """
        for (_wg_addr, netinfo) in self.netinfo.items():
            if netinfo.ip_in_net(cidr):
                return netinfo
        return None

    def refresh_address(self, cidrs:Stringy):
        """
        Check if address needs updating and update if needed.
        Needs to have address for each server network and have correct prefixlen
        address is either str or [str]
        returns (address:[str], changed:bool)
        """
        if not isinstance(address, list):
            address = [address]

        addresses = []
        netinfo_ok = []
        for cidr in cidrs:
            change = False
            ipt = cidr_iptype(cidr)
            if not ipt:
                print(f' refresh address : bad ip {cidr} - ignored')
                continue

            addr = cidr_to_net(cidr)
            prefix = addr.prefixlen

            if (ipt == 'ip4' and prefix != self.prefixlen_4) or (ipt == 'ip6' and prefix != self.prefixlen_6):
                change = True

            netinfo = self.get_netinfo(cidr)
            if netinfo:
                if change:
                    netinfo.mark_address_unavail(cidr)
                else:
                    addresses.append(addr)
                    netinfo_ok.append(netinfo)

        #
        # refresh if needed
        #
        change = False
        for (_wg_addr, netinfo) in self.netinfo.items():
            if netinfo not in netinfo_ok:
                change = True
                nets = netinfo.find_address(self.prefixlen_4,self.prefixlen_6)
                if nets:
                    for net in nets:
                        addresses.append(str(net))
                else:
                    print(' refresh : failed getting new address')

        return (addresses, change)
