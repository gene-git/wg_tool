# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Managa data paths.

All database Files reside under the top level work-dir:

<work-dir>/
    # Internal Data structure.
    Data/<vpn-name>/
        Vpn.info
        <acct-1>/prof-1.prof, prof-2.prof, ...
        <acct-2>/prof-1.prof, prof-2.prof, ...
            ...
        <acct-X>/prof-1.prof, prof-2.prof, ...
        <acct-Y>/prof-1.prof, prof-2.prof, ...

    # wiregoud configs
    Data-wg/<vpn-name>/
        /qr/prof-1.png, prof.png ...
        <acct-1>/prof-1-gw1.conf, prof-1-gw2.conf, prof-2-gw1.conf, ...
        <acct-2>/prof-1-gw1.conf, prof-2-gw2.conf, ...
                        ...

Wireguard section for each acct and profile has one config
per profile-gateway.
E.g. If some vpn has 1 client profile cl1, and 2 gateways gw1 and gw2,
there will be 2 client profiles:
 - cl1-gw1 : interface => gw,  acct = gw2
 - cl1-gw2 : interface => gw2, acct = gw1
and 2 gw profiles:
 - gw1 with accts = gw2, cl1-gw1
 - gw2 with accts = gw1, cl1-gw2

"""
import os

from utils import Msg
from utils import dir_list
from utils import make_dir_path
from ids import Identity

from .constants import (DATA_DIR, WG_DATA_DIR, DB_DIR, EDIT_DIR)


def get_edit_dir(work_dir: str) -> str:
    """
    Directory where Edit/Mod files are written
    """
    edit_dir = os.path.join(work_dir, EDIT_DIR)
    return edit_dir


def get_db_name() -> str:
    """
    DIrectory name for database history
    """
    return DB_DIR


def get_top_dir(work_dir: str) -> str:
    """
    The top level data dir.
    """
    topdir = os.path.join(work_dir, DATA_DIR)
    if not make_dir_path(topdir):
        Msg.warn(f'Error creating {topdir}\n')
    return topdir


def get_top_wg_dir(work_dir: str) -> str:
    """
    The top level data dir.
    """
    wg_topdir = os.path.join(work_dir, WG_DATA_DIR)
    if not make_dir_path(wg_topdir):
        Msg.warn(f'Error creating {wg_topdir}\n')
    return wg_topdir


def get_vpn_dir(work_dir: str, vpn_name: str) -> str:
    """
    Return the top dir where acct data stored.
    work_dir and data_dir must exist (we check in opts.check)
    """
    top_dir = get_top_dir(work_dir)
    vpn_dir = os.path.join(top_dir, vpn_name)
    if not make_dir_path(vpn_dir):
        Msg.warn(f'Error creating {vpn_dir}\n')
    return vpn_dir


def get_wg_vpn_dir(work_dir: str, vpn_name: str) -> str:
    """
    Return the top dir where wireguard server configs data stored.
    work_dir and data_dir must exist (we check in opts.check)
    """
    wg_dir = os.path.join(work_dir, WG_DATA_DIR, vpn_name)
    return wg_dir


def get_acct_names(work_dir: str, vpn_name: str) -> tuple[str, list[str]]:
    """
    Get directory and list of acct names for vpn_name.
    Peer is a directory name.

    Returns:
        tuple[topdir: str, names: list[str]]

    e.g.
        ["<work_dir>/<data>/<vpn1>/",
         ['gateway-1', 'gw-2', 'bob', 'sue', 'jane']
        ]
    """
    vpn_dir = get_vpn_dir(work_dir, vpn_name)
    (_files, name_dirs, _links) = dir_list(vpn_dir, which='name')

    clean_name_dirs: list[str] = []
    for name in name_dirs:
        if Identity.is_valid_name(name):
            clean_name_dirs.append(name)

    return (vpn_dir, clean_name_dirs)


def get_vpn_names(work_dir: str) -> list[str]:
    """
    Get list of vpn names from work_dir/<vpn>

    Returns:
        list[vpn_names: str]:
    """
    top_dir = get_top_dir(work_dir)
    (_files, dir_names, _links) = dir_list(top_dir, which='name')

    # Directory must have Vpn.info file to be a vpn.
    vpn_names: list[str] = []
    for name in dir_names:
        info = os.path.join(top_dir, name, 'Vpn.info')
        if os.path.isfile(info):
            vpn_names.append(name)

    return vpn_names


def get_vpninfo_file(work_dir: str, vpn_name: str) -> str:
    """
    work-dir/vpn/Vpn.info
    """
    vpn_dir = get_vpn_dir(work_dir, vpn_name)
    info_file = os.path.join(vpn_dir, 'Vpn.info')
    return info_file


def get_vpnpsk_file(work_dir: str, vpn_name: str) -> str:
    """
    work-dir/vpn/Vpn.info
    """
    vpn_dir = get_vpn_dir(work_dir, vpn_name)
    psk_file = os.path.join(vpn_dir, 'Vpn.psk')
    return psk_file


def get_etc_dir(_work_dir: str) -> str:
    """
    /etc/wireguard
    """
    etc_dir = '/etc/wireguard'
    return etc_dir


def saved_options_path(work_dir: str) -> str:
    """
    The file where options get saved
    """
    top_dir = get_top_dir(work_dir)
    saved_opts_path = os.path.join(top_dir, 'saved_options')
    return saved_opts_path


def get_file_names(acct_path: str, suffix: str) -> list[str]:
    """
    From acct directory path, return list of file or link names.

    Files are filtered to include only those ending with "suffix".
    """
    file_names: list[str] = []
    (files, _dirs, links) = dir_list(acct_path, which='name')
    for file in files + links:
        if suffix:
            if file.endswith(suffix):
                file_names.append(file)
        else:
            file_names.append(file)
    return file_names
