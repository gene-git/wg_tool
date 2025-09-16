# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Peer directory rename
"""
import os

from utils import os_unlink

from .paths import get_vpn_dir
from .paths import get_wg_vpn_dir


def unlink_profile(work_dir: str,
                   vpn_name: str,
                   acct_name: str,
                   prof_name: str) -> bool:
    """
    Remove the symlink for vpn.acct.prof
    """
    #
    # Data
    #
    vpn_dir = get_vpn_dir(work_dir, vpn_name)
    acct_dir = os.path.join(vpn_dir, acct_name)
    prof_link = os.path.join(acct_dir, f'{prof_name}.prof')
    os_unlink(prof_link)

    #
    # Data-wg
    #
    wg_vpn_dir = get_wg_vpn_dir(work_dir, vpn_name)
    wg_acct_dir = os.path.join(wg_vpn_dir, acct_name)

    # standard config
    wg_conf_link = os.path.join(wg_acct_dir, f'{prof_name}.conf')
    wg_qr_link = os.path.join(wg_acct_dir, 'qr', f'{prof_name}.png')
    os_unlink(wg_conf_link)
    os_unlink(wg_qr_link)

    # Alt config
    wg_alt_conf_link = os.path.join(wg_acct_dir, 'Alt', f'{prof_name}.conf')
    wg_alt_qr_link = os.path.join(wg_acct_dir, 'Alt', 'qr', f'{prof_name}.png')
    os_unlink(wg_alt_conf_link)
    os_unlink(wg_alt_qr_link)

    return True
