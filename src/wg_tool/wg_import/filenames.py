# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
List of profiles
"""
import os

from utils import dir_list


def files_to_import(work_dir: str, vpn_name: str) -> list[str]:
    """
    Make a list of all file paths

        work_dir/vpn_name/<account>/<profile>.conf

    Returns list of file paths that match this format.
    """
    flist: list[str] = []
    topdir = os.path.join(work_dir, vpn_name)

    #
    # account paths
    #
    (_files, acct_dirs, _links) = dir_list(topdir, which='path')

    for acct_dir in acct_dirs:
        (files, _dirs, links) = dir_list(acct_dir, which='path')

        for file in files + links:
            if file.endswith('.conf'):
                flist.append(file)

    return flist
