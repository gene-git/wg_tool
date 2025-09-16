# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Helper for modify_merge()
"""
from vpn import Vpn
from peers import Profile
# from utils import Msg

from .vpns_base import VpnsBase


def tag_to_vpn_prof(vpns: VpnsBase, tag: str
                    ) -> tuple[Vpn | None, Profile | None]:
    """
    From tag.
    If tag is a vpn tag return (vpn, None)
    If tags is profile tag, then return (vpn, prof)
    If neither return (None, None)
    Args:
        vpns (VpnsBase):

        tag (str):

    Returns:
            (vpn: Vpn | None, prof: Profile | None)
    """
    if not tag:
        return (None, None)

    #
    # Check if its a vpn tag
    #
    for (_vpn_name, vpn) in vpns.vpn.items():
        if vpn.vpninfo.tag == tag:
            return (vpn, None)

    #
    # Next check for profile tag
    #
    for (_vpn_name, vpn) in vpns.vpn.items():
        prof = vpn.tag_to_prof(tag)
        if prof:
            return (vpn, prof)
    return (None, None)
