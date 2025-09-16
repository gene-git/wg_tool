# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Create a new vpn/acct/profile
"""
# pylint: disable=too-many-locals, too-many-branches, too-many-statements
from py_cidr import Cidr

from utils import Msg
from net import internet_networks

from .vpns_base import VpnsBase
from .modify_ids_to_idents import ids_to_prof_idents


def modify_nets(vpns: VpnsBase) -> bool:
    """
    Create new item.
    Can be applied to vpn(s) or vpn.acct or vpn.acct.profile
    Required: All target id passed as positional
              parameters (opts.idents)
    Returrns True if all succeeded
    Nets may contain cidr blocks or the string "internet".
    """
    opts = vpns.opts
    #
    # who: IDs are passed in as positional parameters
    #
    if not opts.idents.ids:
        return True

    #
    # what : config requires only one of these options
    #        so we dont need to check this again here.
    #
    what: str = ''

    wanted: bool = False
    offered: bool = False
    if opts.nets_wanted_add:
        mod_nets = opts.nets_wanted_add
        what = 'add'
        wanted = True

    elif opts.nets_offered_add:
        mod_nets = opts.nets_offered_add
        what = 'add'
        offered = True

    elif opts.nets_wanted_del:
        mod_nets = opts.nets_wanted_del
        what = 'del'
        wanted = True

    elif opts.nets_offered_del:
        mod_nets = opts.nets_offered_del
        what = 'del'
        offered = True

    else:
        # should not have been called
        Msg.warn('Modify nets but no option set.\n')
        return True

    if not mod_nets:
        # nothing to do
        return True

    #
    # Check for "internet" in input list of networks
    # can be string "internet" or 0.0.0.0/0 or ::/0
    #
    (internet, mod_nets) = _check_for_internet(mod_nets)

    #
    # Check for valid network cidr blocks
    #
    if not _check_nets_valid(mod_nets):
        return False

    #
    # Get list of profiles matchin command line ids
    #
    ids = ids_to_prof_idents(opts, vpns)

    changed: bool
    for ident in ids:
        vpn_name = ident.vpn_name
        acct_name = ident.acct_name
        prof_name = ident.prof_name

        vpn = vpns.vpn[vpn_name]
        (_acct, prof) = vpn.find_acct_prof(acct_name, prof_name)
        # add if not there and mark acct/prof changed
        if not prof:
            # should not happen
            Msg.err(f'Error - lost {ident.id_str}\n')
            return False

        if wanted:
            (changed, new_nets) = _mod_nets(what, prof.nets_wanted, mod_nets)
            if changed:
                prof.nets_wanted = new_nets
                prof.changed = True

            (changed, internet_wanted) = _mod_internet(
                    what, prof.internet_wanted, internet)
            if changed:
                prof.internet_wanted = internet_wanted
                prof.changed = True

        elif offered:
            (changed, new_nets) = _mod_nets(what, prof.nets_offered, mod_nets)
            if changed:
                prof.nets_offered = new_nets
                prof.changed = True

            (changed, internet_offered) = _mod_internet(
                    what, prof.internet_offered, internet)
            if changed:
                prof.internet_offered = internet_offered
                prof.changed = True

    return True


def _mod_internet(what: str, old_value: bool, internet: str
                  ) -> tuple[bool, bool]:
    """
    what is add, old is current state. internet is 'set' means
    we are doing something otherwise not.
    e.g. if old_value is True,
            what is add - no changed
            what is del - then remove it
         if old_value is False
            what is add - change
            what is del - nothing to do
    """
    new_value: bool = old_value
    changed: bool = False
    if internet != 'set':
        return (changed, old_value)

    if old_value:
        if what == 'del':
            changed = True
            new_value = False
    else:
        if what == 'add':
            changed = True
            new_value = True

    return (changed, new_value)


def _mod_nets(what: str,
              old: list[str],
              mod: list[str]
              ) -> tuple[bool, list[str]]:
    """"
    If what is 'add' then
        Add/merge mod to old and return the result
    if what is 'del' then
        Remove mod from old and return result
    Returns (changed, new_list)
    """
    nets: list[str] = []
    if not mod:
        return (False, old)

    if what == 'del':
        remove_set = set(mod)
        nets = [net for net in old if net not in remove_set]
    else:
        nets = list(set(old + mod))

    changed = False
    if set(nets) != set(old):
        changed = True
    return (changed, nets)


def _check_for_internet(nets: list[str]) -> tuple[str, list[str]]:
    """
    If internet in list of nets, mark internet='yes'
    and remove from the list of networks.
    """

    internet = ''
    mod_nets: list[str] = []
    if not nets:
        return (internet, mod_nets)

    internets = internet_networks()
    for net in nets:
        if net in internets or net.lower() == 'internet':
            internet = 'set'
        else:
            mod_nets.append(net)

    return (internet, mod_nets)


def _check_nets_valid(nets: list[str]) -> bool:
    """
    Return true of each network is valid
    """

    for net in nets:
        if not Cidr.is_valid_cidr(net):
            Msg.err(f'Error - invalid network: {net}\n')
            return False
    return True
