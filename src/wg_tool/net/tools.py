# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
# pylint: disable = too-few-public-methods
# pylint disable = too-many-instance-attributes
"""
Net tools
"""
from py_cidr import Cidr


def cidr_in_cidrs(cidr: str, cidrs: list[str]) -> bool:
    """
    Return True if cidr in list of cidrs.
    "in" means same as or subnet of.
    """
    if not cidr:
        return False

    if not cidr:
        return True

    if cidr in cidrs:
        return True

    nets = Cidr.cidrs_to_nets(cidrs)
    if Cidr.cidr_is_subnet(cidr, nets):
        return True
    return False


def internet_networks() -> list[str]:
    """
    Allowed Internet Net Blocks
    Return list of ipv4/ipv6 internet network blocks.
    i.e. everthing unless we want to restrict
    """
    ip4 = ["0.0.0.0/0"]
    ip6 = ["::/0"]
    nets = ip4 + ip6
    return nets
