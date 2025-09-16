# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Set wireguard address
"""

from utils import Msg
from net import NetWorks

from .profile_base import ProfileBase


def set_wireguard_address(networks: NetWorks, prof: ProfileBase) -> bool:
    """
    Ensure that profile has a "wireguard" address.
    This is the it's IP address but with prefix len set to the vpn
    network prefixlen while keeping host bits set.

    Address + vpninfo -> AddressWg

    Returns True if all well.
    """

    if not prof.Address:
        # nothing to do
        return True

    address_wg: list[str] = []
    for addr in prof.Address:
        addr_wg = networks.addr_to_wg_addr(addr)
        if addr_wg:
            address_wg.append(addr_wg)
        else:
            Msg.err(f'Error: profile ip {addr} not part of vpn network\n')
            return False

    prof.AddressWg = address_wg
    return True
