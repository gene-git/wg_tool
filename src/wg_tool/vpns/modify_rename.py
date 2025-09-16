# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Create a new vpn/acct/profile
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-return-statements
from config import Opts
from utils import Msg
from data import rename_vpn_dir
from ids import Identity

from .vpns_base import VpnsBase


class _Requests:
    """ what to rename """
    def __init__(self, opts: Opts):
        self.rename_vpn = False
        self.rename_acct = False
        self.rename_prof = False

        self.old_id = Identity()
        self.old_id.from_str(opts.ident)

        self.new_id = Identity()
        self.new_id.from_str(opts.to_ident)

        old_name = self.old_id.vpn_name
        new_name = self.new_id.vpn_name
        if old_name and old_name != new_name:
            self.rename_vpn = True

        old_name = self.old_id.acct_name
        new_name = self.new_id.acct_name
        if old_name and old_name != new_name:
            self.rename_acct = True

        old_name = self.old_id.prof_name
        new_name = self.new_id.prof_name
        if old_name and old_name != new_name:
            self.rename_prof = True


def modify_rename(vpns: VpnsBase) -> bool:
    """
    Rename opts.ident -> opts.to_ident.

    Renames must be done in order
        vpn -> acct -> profile
    """
    Msg.info('Mod rename:\n')

    opts = vpns.opts

    #
    # What is being renamed.
    #
    requests = _Requests(opts)
    old_id = requests.old_id
    new_id = requests.new_id

    #
    # Input Checks
    #
    if not _input_checks(vpns, requests):
        return False

    #
    # Do rename(s)
    #
    vpn_name = old_id.vpn_name
    vpn = vpns.vpn[vpn_name]
    if requests.rename_vpn:
        new_name = new_id.vpn_name
        if not _vpns_rename_vpn(vpns, vpn_name, new_name):
            return False
        vpn = vpns.vpn[new_name]
        vpn_name = new_name

    acct_name = old_id.acct_name
    if requests.rename_acct:
        new_name = new_id.acct_name

        if not vpn.rename_acct(acct_name, new_name):
            return False
        acct_name = new_name

    prof_name = old_id.prof_name
    if requests.rename_prof:
        new_prof_name = new_id.prof_name
        if not vpn.rename_prof(acct_name, prof_name, new_prof_name):
            return False
    return True


def _input_checks(vpns: VpnsBase, req: _Requests) -> bool:
    """
    Validate input
        vpn -> vpn      (minimum)
        vpn:acct -> vpn:acct
        vpn:acct:prof -> vpn_prof
    """
    opts = vpns.opts
    old_id = req.old_id
    new_id = req.new_id

    #
    # Input Checks
    #
    if not opts.ident:
        Msg.err('  Error rename needs a ident\n')
        return False

    if not opts.to_ident:
        Msg.err('  Error rename needs a to-ident\n')
        return False

    if not old_id.vpn_name:
        Msg.err('  Error missing vpn_name to rename\n')
        return False

    if not new_id.vpn_name:
        Msg.err('  Error missing target vpn_name to rename to\n')
        return False

    #
    # Check anything to be renamed has orig and new
    #
    if not _name_pair('vpn', old_id.vpn_name, new_id.vpn_name):
        return False

    if not _name_pair('acct', old_id.acct_name, new_id.acct_name):
        return False

    if not _name_pair('prof', old_id.prof_name, new_id.prof_name):
        return False

    #
    # Check vpn to be renamed exists
    #
    if old_id.vpn_name and old_id.vpn_name not in vpns.vpn:
        Msg.err(f'  Error vpn {old_id.vpn_name} not found\n')
        return False

    #
    # If rename vpn_name, make sure the target does not exist
    #
    if old_id.vpn_name != new_id.vpn_name:
        if new_id.vpn_name in vpns.vpn:
            Msg.err(f'  Error target name {new_id.vpn_name} already exists\n')
            return False
    return True


def _name_pair(which: str, a: str, b: str) -> bool:
    """
    old and new must come in pairs
    """
    if (a and not b) or (b and not a):
        Msg.err(f'Error: need both orig and new {which} name\n')
        Msg.plain(f'  {a} vs {b}')
        return False
    return True


def _vpns_rename_vpn(vpns: VpnsBase, old_name: str, new_name: str) -> bool:
    """
    Rename a vpn
    Returns true if all ok
    Not a vpns method so we avoid circular reference back to vpns
    """
    if old_name not in vpns.vpn:
        Msg.err(f'Error vpn {old_name} not found\n')
        return False

    if new_name in vpns.vpn:
        Msg.err(f'Error vpn {new_name} already exists\n')
        return False

    vpn = vpns.vpn[old_name]
    vpns.vpn[new_name] = vpn
    del vpns.vpn[old_name]

    if not vpn.rename_vpn(new_name):
        return False

    work_dir = vpns.opts.work_dir
    if not rename_vpn_dir(work_dir, old_name, new_name):
        return False
    return True
