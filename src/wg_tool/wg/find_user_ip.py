# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Find available IP address for new user.
"""

def find_user_ip(wgtool):
    """
    find an available user IP address
    """
    wmsg = wgtool.wmsg
    ipinfo = wgtool.ipinfo
    wg_address = wgtool.server.Address

    num_nets = len(wg_address)

    # get list of addresses 1 per server network
    address = ipinfo.find_address()
    num_address = 0
    if address:
        num_address = len(address)

    if num_address == 0:
        wmsg ('Not enough available ips - increase server network blocks or remove a user')
    elif num_address < num_nets:
        wmsg(f'Server uses {num_nets} networks, only {num_address} available')
        wmsg(' increase server CIDR block(s) or shorten user prefixlen')
    return address

def is_user_address_available(ipinfo, address):
    """
    check if ip is available
    """
    if not isinstance(address, list):
        address = [address]
    all_avail = True
    for one in address:
        avail = ipinfo.is_address_available(one)
        if not avail:
            all_avail = False
    return all_avail
