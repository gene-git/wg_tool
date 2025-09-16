# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Peer directory rename
"""
import os

from utils import Msg

from .paths import get_vpn_dir
from .paths import get_wg_vpn_dir


def _rename_dir(old: str, new: str) -> bool:
    """
    Rename directory
    """
    if not (old and new):
        Msg.warn(f'Cannot rename dir {old} to {new}\n')
        return False

    if not os.path.isdir(old):
        return True
    try:
        os.rename(old, new)
    except OSError as exc:
        Msg.err(f'Error: rename_dir({old}, {new}) : {exc}\n')
        return False

    return True


def rename_vpn_dir(work_dir: str, vpn_name: str, vpn_name_new: str) -> bool:
    """
    Rename vpn dir
    """
    if not (vpn_name and vpn_name_new):
        Msg.err('Error Rename vpn dir. Bad input\n')
        Msg.plain(f' {vpn_name} -> {vpn_name_new}\n')
        return False

    # Data
    old_dir = get_vpn_dir(work_dir, vpn_name)
    new_dir = get_vpn_dir(work_dir, vpn_name_new)
    if not _rename_dir(old_dir, new_dir):
        return False

    # Data_wg
    old_dir = get_wg_vpn_dir(work_dir, vpn_name)
    new_dir = get_wg_vpn_dir(work_dir, vpn_name_new)
    if not _rename_dir(old_dir, new_dir):
        return False
    return True


def rename_acct_dir(work_dir: str,
                    vpn_name: str,
                    acct_name: str,
                    acct_name_new: str) -> bool:
    """
    Rename:
        Data/vpn_name/acct_name -> Data/vpn_name/acct_name_new
        Data_wg/vpn_name/acct_name -> Data_wg/vpn_name/acct_name_new
    """
    if not (vpn_name and acct_name and acct_name_new):
        Msg.err('Error Rename acct dir. Bad input\n')
        Msg.plain(f' Vpn {vpn_name}: {acct_name} -> {acct_name_new}\n')
        return False

    # Data
    vpn_dir = get_vpn_dir(work_dir, vpn_name)
    old_dir = os.path.join(vpn_dir, acct_name)
    new_dir = os.path.join(vpn_dir, acct_name_new)
    if not _rename_dir(old_dir, new_dir):
        return False

    # Data_wg
    wg_vpn_dir = get_wg_vpn_dir(work_dir, vpn_name)
    old_dir = os.path.join(wg_vpn_dir, acct_name)
    new_dir = os.path.join(wg_vpn_dir, acct_name_new)
    if not _rename_dir(old_dir, new_dir):
        return False
    return True


def rename_prof_dir(work_dir: str,
                    vpn_name: str,
                    acct_name: str,
                    prof_name: str,
                    prof_name_new: str) -> bool:
    """
    Rename
        Data/vpn_name/acct_name/
                    prof_name -> prof_name_new
        Data_wg/vpn_name/acct_name/
                    prof_name -> prof_name_new
    """
    if not (vpn_name and acct_name and prof_name and prof_name_new):
        Msg.err('Error Rename acct dir. Invalid input\n')
        txt = f'{prof_name}-> {prof_name_new}'
        Msg.plain(f' Vpn {vpn_name}.{acct_name} {txt}\n')
        return False

    # Data
    vpn_dir = get_vpn_dir(work_dir, vpn_name)
    pdir = os.path.join(vpn_dir, acct_name)
    old_dir = os.path.join(pdir, prof_name)
    new_dir = os.path.join(pdir, prof_name_new)
    if not _rename_dir(old_dir, new_dir):
        return False

    # Data_wg
    wg_vpn_dir = get_wg_vpn_dir(work_dir, vpn_name)
    pdir = os.path.join(wg_vpn_dir, acct_name)
    old_dir = os.path.join(pdir, prof_name)
    new_dir = os.path.join(pdir, prof_name_new)
    if not _rename_dir(old_dir, new_dir):
        return False
    return True
