#!/usr/bin/python
"""
User IP tool
"""
# pylint: disable=too-many-instance-attributes
import netaddr
from netaddr import AddrConversionError,AddrFormatError,NotRegisteredError

class NetInfo:
    """ data for 1 network """
    def __init__(self, wg_address):
        """
        wg_address is in wg format - i.e. IP/cidr_prefix
        e.g. 10.1.1.1/24 where server IP is 10.1.1.1 and network is 10.1.1.0/24
        Server has 1 ip in this network
        """
        self.okay = True
        self.wg_address = wg_address
        self.server_ip = None
        self.server_net = None
        self.iptype = None
        self.ip_net = None

        self.ip_set = netaddr.IPSet([])
        self.ip_used_set = netaddr.IPSet([])

        #
        # Extract network
        #
        try:
            self.ip_net = netaddr.IPNetwork(wg_address)

        except (AddrConversionError,AddrFormatError,NotRegisteredError) :
            print(f'Error with address {wg_address}')
            self.okay = False
            return

        self.server_ip = self.ip_net.ip
        if netaddr.valid_ipv4(str(self.server_ip)):
            self.iptype = 'ip4'
        elif netaddr.valid_ipv6(str(self.server_ip)):
            self.iptype = 'ip6'
        else:
            print(f'Bad wg address {wg_address}')
            self.okay = False
            return

        self.server_net = self.ip_net.cidr

        #
        # Make ip_set of available addresses
        #  - remove server IP
        #  - remove network and broadcast IPs
        #
        self.ip_set = netaddr.IPSet([wg_address])
        self.ip_set.remove(self.ip_net.network)
        self.ip_set.remove(self.ip_net.broadcast)
        self.ip_set.remove(self.server_ip)

    def add_used_addr(self, ip_addr):
        """
        If cidr in net then add to used list
           return true if added else false
        """
        if ip_addr in self.ip_net :
            self.ip_used_set.add(ip_addr)
            return True
        return False

    def remove_used_addr(self, ip_addr):
        """
        If cidr in net then add to used list
           return true if added else false
        """
        if ip_addr in self.ip_used_set :
            self.ip_used_set.remove(ip_addr)

    def find_address(self, prefixlen_4, prefixlen_6):
        """
        Find available ip/prefixlen
        """
        ip_avail = self.ip_set
        ip_avail -= self.ip_used_set

        prefixlen = prefixlen_4
        if self.iptype == 'ip6':
            prefixlen = prefixlen_6

        if prefixlen <= 0:
            return None

        cidr_found = None
        for cidr in ip_avail.iter_cidrs():
            if prefixlen >= cidr.prefixlen:
                cidr_found = cidr
                cidr_found.prefixlen = prefixlen
                break

        if cidr_found:
            self.ip_used_set.add(cidr_found)
        else:
            print(f'Failed to find available {self.iptype} / {prefixlen}')
        return cidr_found

    def address_available(self, address:str):
        """ check if address in net and available """
        ip_avail = self.ip_set - self.ip_used_set
        ip_addr = netaddr.IPNetwork(address)
        avail = False
        if ip_addr in self.ip_net and ip_addr in ip_avail:
            avail = True
        return avail

    def add_used_address(self, cidr):
        """
        Add cidr to list of used addresses
        """
        if cidr in self.ip_net:
            if cidr not in self.ip_used_set:
                self.ip_used_set.add(cidr)
                return True
        return False

class IpInfo:
    """ manage user ips """
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

    def find_address(self):
        """
        Returns list of addresses for each server network
        """
        addresses = []
        for (_wg_addr, netinfo) in self.netinfo.items():
            addr = netinfo.find_address(self.prefixlen_4, self.prefixlen_6)
            if addr:
                addresses.append(str(addr))
            else:
                self.okay = False

        return addresses

    def address_available(self, address):
        """
        check if address (ip or cidr) is available
        """
        cidr = netaddr.IPNetwork(address)
        netinfo = self.get_netinfo(cidr)
        if not netinfo:
            print(f'Error: Address {address} is not part of server network')
            return False

        if netinfo.address_available(address):
            return True
        return False

    def add_used_addresses(self, cidrs:[str]):
        """
        Add cidr_str to list of used
        Must be in one of the known nets
        """
        for cidr_str in cidrs:
            cidr = netaddr.IPNetwork(cidr_str)
            added = False
            for (_wg_addr, netinfo) in self.netinfo.items():
                added = netinfo.add_used_address(cidr)
                if added:
                    break
            if not added:
                print(f'Warning: Address {cidr_str} not in server networks - ignored')
                print('         Cannot add to list of used IP addresses')

    def remove_used_addresses(self, cidrs:[str]):
        """
        Remove cidr_str from list of used
        Must be in one of the known nets
        """
        for cidr_str in cidrs:
            cidr = netaddr.IPNetwork(cidr_str)
            netinfo = self.get_netinfo(cidr)
            if netinfo:
                netinfo.remove_used_address(cidr)
            else :
                print(f'Error: Address {cidr_str} not in server networks')
                self.okay = False
        return self.okay

    def get_netinfo(self, cidr):
        """
        Return netinfo that cidr belongs to or None
        """
        for (_wg_addr, netinfo) in self.netinfo.items():
            if cidr in netinfo.ip_net:
                return netinfo
        return None

    def refresh_address(self, address):
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
        for addr in address:
            change = False
            cidr = netaddr.IPNetwork(addr)
            prefixlen = cidr.prefixlen

            if netaddr.valid_ipv4(str(cidr.ip)) and prefixlen != self.prefixlen_4:
                change = True
            elif netaddr.valid_ipv6(str(cidr.ip)) and prefixlen != self.prefixlen_6:
                change = True

            netinfo = self.get_netinfo(cidr)
            if netinfo:
                if change:
                    netinfo.remove_used_addr(cidr)
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
                address = netinfo.find_address(self.prefixlen_4,self.prefixlen_6)
                addresses.append(str(address))

        return (addresses, change)
