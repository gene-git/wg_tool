# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Create a new vpn/acct/profile
"""
# pylint: disable=too-many-return-statements
from utils import Msg
from ids import Identity

from .vpns_base import VpnsBase


def modify_state(vpns: VpnsBase) -> bool:
    """
    Handle active/hidden states.
    """
    opts = vpns.opts
    active: bool | None = None
    if opts.active:
        active = True

    elif opts.not_active:
        active = False

    hidden: bool | None = None
    if opts.hidden:
        hidden = True
        active = False

    elif opts.not_hidden:
        hidden = False
    #
    # IDs passed as positional parameters
    #
    ids = opts.idents.ids
    if not ids:
        return True

    for ident in ids:
        if not _set_state(vpns, ident, hidden, active):
            return False
    return True


def _set_state(vpns: VpnsBase,
               ident: Identity,
               hidden: bool | None,
               active: bool | None) -> bool:
    """
    Set active state for one ident
    Returns True if all good.
    """
    vpn_name = ident.vpn_name
    acct_name = ident.acct_name
    prof_name = ident.prof_name

    if not vpn_name:
        # nothing to do
        return True
    #
    # vpn
    #
    vpn = vpns.vpn.get(vpn_name)
    if not vpn:
        Msg.err(f'set_state error: Unkown vpn: {vpn_name}\n')
        return False
    #
    # Applies to vpn
    #
    if not (acct_name and prof_name):
        if hidden is not None:
            vpn.set_hidden(hidden)

        if active is not None:
            vpn.set_active(active)
        return True
    #
    # Applies to acct
    #
    (acct, prof) = vpn.find_acct_prof(acct_name, prof_name)
    if not acct:
        Msg.err(f'set_active error unkown acct: {ident.id_str}\n')
        return False

    if not prof_name:
        if hidden is not None:
            acct.set_hidden(hidden)

        if active is not None:
            acct.set_active(active)
        return True
    #
    # Applies to profile
    #
    if not prof:
        Msg.err(f'set_active error. Unkown profile {ident.id_str}\n')
        return False

    if hidden is not None:
        prof.set_hidden(hidden)

    if active is not None:
        prof.set_active(active)

    return True
