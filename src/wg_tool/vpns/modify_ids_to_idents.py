# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Helper routine
Command line ID to list of identities
Used my modify_state, modify_nets
"""
from utils import Msg
from config import Opts
from ids import Identity

from .vpns_base import VpnsBase


def ids_to_prof_idents(opts: Opts, vpns: VpnsBase) -> list[Identity]:
    """
    Map command line IDs to list of idents.
    We permit a little freedom here by allowing missing profile
    to mean all profiles, and missing both account and profile
    to mean all accounts and all profiles.
    Alternatively we could require or use wildcard.
    Get
        (vpn, '', '') -> vpn all accounts and all profiles
        (vpn, acct, '') -> vpn.acct all profiles
        (vpn, acct, prof) jst one
    """
    ids: list[Identity] = []

    for ident in opts.idents.ids:
        vpn_name = ident.vpn_name
        acct_name = ident.acct_name
        prof_name = ident.prof_name

        if vpn_name not in vpns.vpn:
            Msg.err(f'Unknown vpn: {vpn_name}\n')
            ids = []
            return ids

        vpn = vpns.vpn[vpn_name]
        if acct_name:
            acct = vpn.accts[acct_name]
            if prof_name:
                if prof_name in acct.profile:
                    prof = acct.profile[prof_name]
                    ids.append(prof.ident)
                    continue
                Msg.err(f'Unknown prof: {ident.id_str}\n')
                ids = []
                return ids

            for prof in list(acct.profile.values()):
                ids.append(prof.ident)
            continue

        for (acct_name, acct) in vpn.accts.items():
            for prof in list(acct.profile.values()):
                ids.append(prof.ident)

    return ids
