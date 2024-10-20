# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
'''
IP Network Tools
'''
import re
import ipaddress
from ipaddress import (AddressValueError, NetmaskValueError)
from ipaddress import (IPv4Network, IPv6Network, IPv4Address, IPv6Address)

def address_to_net(addr:str|IPv4Network|IPv6Network|IPv4Address|IPv6Address) -> IPv4Network|IPv6Network|None:
    '''
    Make net from address
    '''
    if not addr:
        return None

    if isinstance(addr, (IPv4Network, IPv6Network)):
        return addr

    if isinstance(addr, (str, IPv4Address, IPv6Address)):
        return ipaddress.ip_network(addr)

    return None

def net_in_net(net1:IPv4Network|IPv6Network, net2:IPv4Network|IPv6Network) -> bool:
    '''
    Check if net1 is in net2
    '''
    if not net1 or not net2:
        return False

    ipt1 = address_iptype(net1)
    ipt2 = address_iptype(net2)

    if ipt1 != ipt2:
        return False

    is_in_net = net1.subnet_of(net2)
    return is_in_net

def ip_to_address(ip:str) -> IPv4Address|IPv6Address|None:
    '''
    Return ip address of given ip.
    If ip has prefix and host bits set, we strip the prefix first
    '''
    if not ip:
        return None

    ipin = ip
    if '/' in ip:
        ipin = re.sub(r'/.*$', '',  ip)

    try:
        addr = ipaddress.ip_address(ipin)
    except AddressValueError:
        addr = None

    return addr

def cidr_to_net(cidr:str, strict:bool=False) -> IPv4Network | IPv6Network | None:
    '''
    Returns the network associated with the cidr string
     - if strict is True then invalid if host bits are set.
     - see ipaddress docs
    '''
    if not cidr:
        return None

    return ipaddress.ip_network(cidr, strict=strict)

def is_valid_ip4(address:str) -> bool:
    ''' check if valid address or cidr '''
    try:
        _check = ipaddress.IPv4Network(address, strict=False)
        return True
    except (AddressValueError, NetmaskValueError, TypeError):
        return False

def is_valid_ip6(address:str) -> bool:
    ''' check if valid address or cidr '''
    try:
        _check = ipaddress.IPv6Network(address, strict=False)
        return True
    except (AddressValueError, NetmaskValueError, TypeError):
        return False

def is_valid_cidr(address:str) -> bool:
    '''
    check if valid ip address
     - returns True/False
    '''
    if not address:
        return False
    if is_valid_ip4(address) or is_valid_ip6(address):
        return True
    return False

def cidr_iptype(address:str) -> str|None :
    '''
    Input:
        ip address or cidr string
     Output
        'ip4' or 'ip6' or None
    '''
    if not address:
        return None
    if is_valid_ip4(address) :
        return 'ip4'
    if is_valid_ip6(address):
        return 'ip6'
    return None

def address_iptype(addr:IPv4Address|IPv6Address|IPv4Network|IPv6Network) -> str|None:
    '''
    Input:
        address or network
    Output
        'ip4' 'ip6' or None
    '''
    if not addr:
        return None
    ipt = type(addr)
    if ipt in (IPv4Address,IPv4Network):
        return 'ip4'
    if ipt in (IPv6Address,IPv6Network):
        return 'ip6'
    return None

def sort_nets(nets:[IPv4Network|IPv6Network]) -> [IPv4Network|IPv6Network]:
    '''
    Sort the list of cidr strings
    '''
    if not nets:
        return nets
    nets_sorted = sorted(nets, key=ipaddress.get_mixed_type_key)
    return nets_sorted

def sort_cidrs(cidrs:[str]) -> [str]:
    '''
    Sort the list of cidr strings
    '''
    nets = cidrs_to_nets(cidrs)
    nets_sorted = sort_nets(nets)
    cidrs_sorted = nets_to_cidrs(nets_sorted)
    return cidrs_sorted

def cidrs_to_nets(cidrs:[str], strict:bool=False) -> [IPv4Network | IPv6Network]:
    '''
    For list of cidr strings return list if ip_network
    '''
    nets = [ipaddress.ip_network(cidr, strict=strict) for cidr in cidrs]
    return nets

def nets_to_cidrs(nets:[IPv4Network | IPv6Network]) -> [str]:
    '''
    List of nets to list of cidr strings
    '''
    cidrs = [str(net) for net in nets]
    return cidrs
