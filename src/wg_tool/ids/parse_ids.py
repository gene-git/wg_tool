# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Map command line input list of:
    vpn.acct.prof

    vpn = vpn name
    acct = acct name
    prof = profile name or comma sep list of profiles

    Acceptable forms are:
        vpn
        vpn.acct
        vpn.acct.prof
    prof can be one name or comma separarated list of names
    If more than one is provided they must all be same information.
    e.g. If one has vpn only they must all have vpn only etc.
"""
# pylint: disable=too-many-locals
from utils import Msg
from .identity import Identity


def parse_ids(names: list[str]) -> tuple[bool, list[Identity]]:
    """
    Parser for command line list of acct id strings

    NB name validity is checked.

    Args:
        names (list[str]):
        Each element of names list: vpn:acct:prof
        Where vpn, acct and profile names must be provided.
        Profile can be one profile or commad separated list of profiles.

    Returns:
        tuple(status: bool, ids: list[Identity]):
        Status is true of all well.
        ids is a list of Identity
    """
    ids: list[Identity] = []

    if not names:
        # empty command line is ok
        return (True, ids)

    #
    # If more than 1 profile, expand names list
    # comma is not valid Identity character
    #
    names_all: list[str] = _expand_profs(names)

    #
    # make Identity from id strings
    #
    names_ok = True
    for name in names_all:
        one_id = Identity()
        one_id.from_str(name)
        if not one_id.validate_names():
            names_ok = False
        ids.append(one_id)

    #
    # Check for consistency and valid names
    #
    if not names_ok:
        return (False, ids)

    if not _consistency_check(ids):
        return (False, ids)

    return (True, ids)


def _expand_profs(names: list[str]) -> list[str]:
    """
    Expand to list if any prof has multiple names
    e.g.
        vpn.acct.p1,p2
    ->
        vpn.acct.p1 vpn.acct.p2

    accept "." or "/" as separator
    """
    names_all: list[str] = []
    for name in names:
        vpn_name = ''
        acct_name = ''
        prof_name = ''

        #
        if '/' in name:
            name = name.replace('/', '.')

        parts = name.split('.', maxsplit=2)
        num_parts = len(parts)

        vpn_name = parts[0]
        if num_parts >= 2:
            acct_name = parts[1]

        if num_parts >= 3:
            prof_name = parts[2]

        if not prof_name:
            names_all.append(name)
            continue

        #
        # if full profile check if 1 profile or more than 1
        # - profiles may be separated by commas.
        #
        multiple_profs = False
        prof_names: list[str] = []
        if prof_name:
            if ',' in prof_name:
                multiple_profs = True
                prof_names = prof_name.split(',')
            else:
                prof_names = [prof_name]

        #
        # build id string
        #
        if not multiple_profs:
            names_all.append(name)
        else:
            vpn_acct = f'{vpn_name}.{acct_name}'
            for aprof in prof_names:
                id_str = f'{vpn_acct}.{aprof}'
                names_all.append(id_str)

    return names_all


def _consistency_check(ids: list[Identity]) -> bool:
    """
    If more than one id, check they are consistent with one another.
    i.e. must be the same form.
    vpn or vpn:acct or vpn:acct:prof
    """
    if not ids or len(ids) == 1:
        return True

    have_vpn = bool(ids[0].vpn_name)
    have_acct = bool(ids[0].acct_name)
    have_prof = bool(ids[0].prof_name)

    for one in ids:
        this_have_vpn = bool(one.vpn_name)
        this_have_acct = bool(one.acct_name)
        this_have_prof = bool(one.prof_name)

        if have_vpn != this_have_vpn:
            # this should never happen
            Msg.err('Inconsistent acct names. Missing vpn\n')
            return False

        if have_acct != this_have_acct:
            Msg.err('Inconsistent acct names. Missing acct\n')
            return False

        if have_prof != this_have_prof:
            Msg.err('Inconsistent acct names. Missing profile\n')
            return False
    return True
