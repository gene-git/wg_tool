# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Create a new vpn/acct/profile
"""
# pylint: disable=too-many-locals
# pylint: disable=too-many-return-statements
from utils import Msg
from ids import Identity

from .vpns_base import VpnsBase
from .modify_save import save_prof_edit


def modify_copy(vpns: VpnsBase) -> bool:
    """
    Copy opts.ident -> opts.to_ident.

    """
    Msg.info('Mod copy:\n')

    opts = vpns.opts

    old_id = Identity()
    old_id.from_str(opts.ident)

    new_id = Identity()
    new_id.from_str(opts.to_ident)

    #
    # Input Checks
    #
    if not _input_checks(vpns, old_id, new_id):
        return False

    #
    # Copy
    #
    vpn_name = old_id.vpn_name
    acct_name = old_id.acct_name
    prof_name = old_id.prof_name

    # source profile
    vpn = vpns.vpn[vpn_name]
    (_xxx, prof) = vpn.find_acct_prof(acct_name, prof_name)

    if not prof:
        Msg.err('Error: no profile to copy from ')
        Msg.plain(f' {old_id.id_str} not found\n')
        return False

    # dest profile
    vpn_name_new = new_id.vpn_name
    acct_name_new = new_id.acct_name
    prof_name_new = new_id.prof_name

    vpn_new = vpns.vpn[vpn_name_new]
    (acct_new, prof_new) = vpn_new.find_acct_prof(acct_name_new, prof_name_new)

    if prof_new:
        Msg.err(f'Error copy dest profile exists already: {new_id.id_str}\n')
        return False

    if not acct_new:
        Msg.plain(f'  Creating new acct {acct_name_new}\n')
        acct_new = vpn_new.add_acct(acct_name_new)
        if not acct_new:
            Msg.err('  failed\n')
            return False

    Msg.plain(' Creating {prof_name_name}\n')
    prof_new = vpn_new.add_acct_prof(acct_name_new, prof_name_new)
    if not prof_new:
        Msg.err(f' Error creating {new_id.id_str}\n')
        return False
    #
    # ready to make the copy
    # and generate new keys
    #
    if not prof_new.copy(prof):
        return False

    #
    # Save new profile so can be edited and merged back
    #
    Msg.plain('Saving new profile for editing')
    return save_prof_edit(opts.work_dir, prof_new)


def _input_checks(vpns: VpnsBase, old_id: Identity, new_id: Identity) -> bool:
    """
    Validate input
        vpn:acct:prof -> vpn:acct:prof
    """
    # opts = vpns.opts

    if not old_id.full():
        Msg.err(f'Copy needs a full orign id profile : got {old_id.id_str}\n')
        return False

    if not new_id.full():
        Msg.err(f'Copy needs a full dest id profile : got {new_id.id_str}\n')
        return False

    #
    # Check orig vpn exists
    #
    if old_id.vpn_name not in vpns.vpn:
        Msg.err(f'  Error orig vpn {old_id.vpn_name} not found\n')
        return False

    #
    # Check dest vpn exists
    # Should we limit orig and dest vpn to be same?
    #
    if new_id.vpn_name not in vpns.vpn:
        Msg.err(f'  Error dest vpn {new_id.vpn_name} not found\n')
        return False
    return True
