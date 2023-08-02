# SPDX-License-Identifier: MIT
# Copyright (c) 2022,2023 Gene C
"""
Find available IP address for new user.
"""
# pylint: disable=C0103
import netaddr

def _used_ip_set(wgtool):
    """
    Return set of all used ips
    """
    used_set = None
    used_ips = []
    if wgtool.users:
        for (_user_name, user) in wgtool.users.items():
            for (_prof_name, profile) in user.profile.items() :
                ip = profile.Address
                used_ips.append(ip)

        if used_ips:
            used_set = netaddr.IPSet(used_ips)

    return used_set

def _find_user_avail_ips(wgtool):
    """
    find an available user IP address
    """
    # pylint:  disable=R0914
    ip_set = None

    serv_ips = wgtool.server.Address
    used_set = _used_ip_set(wgtool)

    for cidr in serv_ips:
        ip_net = netaddr.IPNetwork(cidr)
        ip_set = netaddr.IPSet([cidr])

        #
        # Remove server IP and network/broadcast IPs
        #
        ip_set.remove(ip_net.ip)
        ip_set.remove(ip_net.network)
        ip_set.remove(ip_net.broadcast)

        if used_set:
            ip_set -= used_set
        if ip_set.size > 1:
            break

    return ip_set

def find_user_ip(wgtool):
    """
    find an available user IP address
    """
    wmsg = wgtool.wmsg
    ip_set = _find_user_avail_ips(wgtool)
    address = None
    if ip_set and ip_set.size > 1:
        avail_ip = str(ip_set.iter_cidrs()[0].ip)
        address = f'{avail_ip}/32'
    else:
        wmsg ('Not enough available ips - please increase CIDR block or remove a user')
    return address

def is_user_address_available(wgtool, address):
    """
    check if ip is available
    """
    ip_set = _find_user_avail_ips(wgtool)
    addr_set = netaddr.IPSet([address])
    avail = True
    for each_ip in addr_set:
        if each_ip not in ip_set:
            avail = False
    return avail

def _server_ip_from_address(address):
    """ extract the ip from ip/cidr_mask """
    ip = netaddr.IPNetwork(address).ip
    return str(ip)
