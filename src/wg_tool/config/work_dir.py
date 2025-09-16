# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
When user doesn't specify a work dir we find it
by looking wlong each of the directoris in  "paths".
 - We could also check for config_dir/server/server.conf?
"""
import os

from utils import Msg


def have_permission_rwx(adir: str) -> bool:
    """
    check have rwx on a dir
    NB by default os.access() uses real uid/gid.

    Returns:
        bool:
        True if directory exists and is rwx by effective user
    os.access() can raise NotImplementedError. That should
    never happen on linux, so we let the exception happen.
    """
    dir_mode = os.F_OK | os.X_OK | os.R_OK | os.W_OK
    access = os.access(adir, dir_mode, effective_ids=True)
    return access


def _dir_in_dirlist(child: str, parent_list: list[str]) -> str:
    """
    Return parent/child for any parent in parent_list
    if it exists, else return empty string.
    """
    for parent in parent_list:
        fpath = os.path.join(parent, child)
        if have_permission_rwx(fpath):
            return parent
    return ''


def find_work_dir(paths: str, data_dir: str) -> str:
    """
    For existing setup find the work dir which contains 'data' directory.

    Can always be over-riden with command line option.
    if no config anywhere return empty string.
    """
    nothing = ''
    paths_list: list[str] = []
    if paths:
        paths_list = paths.split(':')

    cwd = './'
    if cwd not in paths_list:
        paths_list.append(cwd)

    work_dir = _dir_in_dirlist(data_dir, paths_list)
    if work_dir:
        return work_dir

    # no work dir - either new config or un-migrated old version
    Msg.warn('No working dir.\n')
    Msg.plainverb('  Checking for older un-migrated configs ... ', level=2)
    old_data_dir = 'configs'
    work_dir = _dir_in_dirlist(old_data_dir, paths_list)
    if work_dir:
        Msg.plain(f'   found pre 8.0 config - "{work_dir}"\n')
        return work_dir

    Msg.plain('  Looks like brand new setup. Please specify work dir:\n')
    Msg.plain('    using "wg-tool --work-dir <dirname>"\n')

    return nothing
