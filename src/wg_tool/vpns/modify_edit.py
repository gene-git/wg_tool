# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Create a new vpn/acct/profile
"""
# pylint: disable=duplicate-code
from utils import Msg
from ids import Identity

from .vpns_base import VpnsBase
from .modify_save import save_prof_edit
from .modify_save import save_vpninfo_edit


def modify_edit(vpns: VpnsBase) -> bool:
    """
    Edit can be:
        vpn -> vpninfo handles
        vpn:acct:profile
    Nothing to edit for vpn:acct

    Returrns True if all succeeded
    """
    Msg.info('Mod edit:\n')

    #
    # ID to edit is passed as opts.ident
    #
    opts = vpns.opts
    if not opts.ident:
        # nothing to edit
        return True

    ident = Identity()
    ident.from_str(opts.ident)
    vpn_name = ident.vpn_name
    acct_name = ident.acct_name
    prof_name = ident.prof_name

    if vpn_name not in vpns.vpn:
        Msg.err(f'vpn {vpn_name} not found\n')
        return False

    vpn = vpns.vpn[vpn_name]

    #
    # vpn or vpn:acct:prof only
    #
    if ident.vpn_only():
        # edit vpn info
        return save_vpninfo_edit(opts.work_dir, vpn.vpninfo)

    if ident.full():
        # profile
        (acct, prof) = vpn.find_acct_prof(acct_name, prof_name)

        if not (acct and prof):
            Msg.err(' Need full Id with vpn.acct.profile\n')
            return False

        return save_prof_edit(opts.work_dir, prof)

    return True
