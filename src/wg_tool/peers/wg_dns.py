# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Convert dns / dns_search list to wireguard DNS format
"""
from py_cidr import Cidr

from dns_resolver import Dns


def dns_to_wg_dns(hosts: list[str], search: list[str]) -> list[str]:
    """
    Wireguard DNS variable must use:

        IP address for dns server
        non-IP address for search domain.

    Args:
        hosts (list[str]):
            list of ip addresses or hostnames

        search (list[str]):
            list of search domains

    Returns one list with hosts as IP addresses combined with search domains.
    """
    #
    # lookup IP addresses if needed
    #
    wg_dns: list[str] = []
    for host in hosts:
        if Cidr.is_valid_cidr(host):
            wg_dns.append(host)
        else:
            ips = Dns.query(host, rr_type='A')
            if ips:
                wg_dns += ips
    #
    # append the search domains
    #
    if search:
        wg_dns += search
    return wg_dns
