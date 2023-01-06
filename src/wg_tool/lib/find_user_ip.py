# SPDX-License-Identifier: MIT
# Copyright (c) 2022,2023 Gene C
"""
Find available IP address for new user.
"""
# pylint: disable=C0103
import netaddr

def _find_user_avail_ips(wgtool):
    """
    find an available user IP address
    """
    # pylint:  disable=R0914
    wmsg = wgtool.wmsg

    serv_ip = wgtool.server.Address
    serv_ip = serv_ip[0]                # only use first (ip4) one

    #
    # Set up range, remove used ips (server and other users)
    #
    ip_net = netaddr.IPNetwork(serv_ip)
    num_ips = len(ip_net)
    low = 1
    high = num_ips - 1
    if high <= low:
        wmsg ('Not enough ips in network - please increase CIDR block')
        return None

    ip_frst = ip_net[low]
    ip_last = ip_net[high]
    ip_range = netaddr.IPRange(ip_frst, ip_last)
    ip_set = netaddr.IPSet(ip_range)

    #
    # excludes : start with server itself
    # for users, faster to subtract 2 sets than do set.remove(ip) one at a time
    #
    ip_set.remove(ip_net.ip)

    #
    # exclude current users
    #
    if wgtool.users:
        used_ips = []
        for (_user_name, user) in wgtool.users.items():
            for (_prof_name, profile) in user.profile.items() :
                ip = profile.Address
                used_ips.append(ip)

        if used_ips:
            used_set = netaddr.IPSet(used_ips)
            ip_set = ip_set - used_set

    return ip_set

def find_user_ip(wgtool):
    """
    find an available user IP address
    """
    wmsg = wgtool.wmsg
    ip_set = _find_user_avail_ips(wgtool)
    address = None
    if len(ip_set) > 1:
        avail_ip = str(list(ip_set)[0])
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
