# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Convert dns / dns_search list to wireguard DNS format
"""
from py_cidr import Cidr

from dns_resolver import Dns


def dns_to_wg_dns(hosts: list[str], include_ipv6: bool) -> list[str]:
    """
    DNS hosts convert any domain names to IP addresses
    since Wireguard DNS variable treats:

        IP address for dns server
        non-IP address for search domain.

    Args:
        hosts (list[str]):
            list of ip addresses or hostnames

        include_ivp6:
            if true then do both A and AAAA lookups

    Returns one list with hosts as IP addresses. Caller may
    add search domains before writing out wireguard DNS variable in
    config.
    """
    #
    # lookup IP addresses for any non-IP address
    #

    # ipv4 and optionally ipv6
    rr_types: tuple[str, ...] = ('A',)
    if include_ipv6:
        rr_types = ('A', 'AAAA',)

    wg_dns: list[str] = []
    for host in hosts:
        if Cidr.is_valid_cidr(host):
            wg_dns.append(host)
            continue
        for rr_type in rr_types:
            ips = Dns.query(host, rr_type=rr_type)
            if ips:
                wg_dns += ips

    return wg_dns
