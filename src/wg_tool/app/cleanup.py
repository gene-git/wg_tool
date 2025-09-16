# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
cleaner
"""
# pylint: disable=too-many-locals
import os
from pathlib import Path

from utils import dir_list
from utils import Msg

from data import get_top_dir
from data import get_top_wg_dir
from data import get_db_name


def cleanup(wgtool):
    """
    Clean up older Data and Data-wg
    Logic is for Data and Data-wg for directories:
        <Data>/<vpns>/<peers>/db/
    Remove older by keeping hist/hist_wg directories.

    Note: Directoty names taken from filesystem.
    """
    opts = wgtool.opts
    num_keep = opts.hist if opts.hist else 5
    num_keep_wg = opts.hist_wg if opts.hist_wg else 3

    data_dir = get_top_dir(opts.work_dir)
    data_wg_dir = get_top_wg_dir(opts.work_dir)
    Msg.hdr('Cleaning history\n')

    #
    # Data
    #
    _clean_vpn_dirs(num_keep, data_dir)

    #
    # Data-wg
    #
    _clean_vpn_dirs(num_keep_wg, data_wg_dir)


def _clean_vpn_dirs(num_keep: int, data_dir: str):
    """
    Identify all peer directories and "db" directoiry
    which has history
    """
    Msg.plainverb(f'  Cleanup of {data_dir}\n', level=3)
    if not data_dir:
        return

    #
    # Vpn.info / Accounts / profiles
    #
    (_fls, vpn_dirs, _lnks) = dir_list(data_dir, which='path')
    for vpn_dir in vpn_dirs:
        #
        # Vpn.info
        #   Data/<vpn>/Vpn.info -> <db>/xxx/Vpn.info
        #
        _clean_one_dir(num_keep, vpn_dir)

        #
        # peers (has 1 or more profile files)
        #   Data/<vpn>/<account>/<prof> -> <db>/xxx/<prof>
        #
        (_fls, peer_dirs, _lnks) = dir_list(vpn_dir, which='path')
        for peer_dir in peer_dirs:
            _clean_one_dir(num_keep, peer_dir)


def _clean_one_dir(num_keep: int, one_dir: str):
    """
    Clean one_dir/db/xxx

    For each symlink file, get its history list and trim it.
    Goal is each symlinked file keeps num_keep of its own history.

    Since dated dirs may be used by more than one symlink file.
    For example, a peer can have multiple profiles.
    Each profile, has it's own history. When a dated ditecory
    is empty, then it can be deleted as well.

    Do not remove any directory that is a symlink target.
    Make a list of db/xx which are link targets
    For each link name find it's history

    one_dir/<linkname> -> <db>/xxx/<linkname>
    find all <y> in <db>/<y>/<linkname> for which <y> is NOT xxx
    """
    Msg.plainverb(f'  Cleanup of {one_dir}\n', level=3)
    removes: list[str] = []

    (_fls, _dirs, all_links) = dir_list(one_dir, which='path')

    db_name = get_db_name()

    for link in all_links:
        # one link at a time as each has its own history.
        # link -> db/<link-targ>/filename
        link_targ = os.readlink(link)
        if db_name not in link_targ:
            # skip if link doesn't point to db_name/xxx/yyy
            continue

        # make sure we always keep xxx the current link points to
        path_obj = Path(link_targ)
        link_subdir = path_obj.parts[-2:][0]

        #
        # Get list of all xxx with same filename as link.
        #   db_dir/xxx/filename
        #
        filename = os.path.basename(link)
        one_db_dir = os.path.join(one_dir, db_name)
        subdirs_all = _subdirs_with_file(one_db_dir, filename)
        if link_subdir in subdirs_all:
            subdirs_all.remove(link_subdir)

        #
        # List of filepaths (without the link target)
        #
        candidates: list[str] = []
        for subdir in subdirs_all:
            fpath = os.path.join(one_dir, db_name, subdir, filename)
            candidates.append(fpath)

        #
        # which of possible are to be removed
        #
        remove_items = _make_remove_list(num_keep, candidates)
        if remove_items:
            removes += remove_items

    #
    # Now we have the list to be removed
    # Go ahead and delete them.
    #
    subdir_list: list[str] = []
    for fpath in removes:
        subdir = os.path.dirname(fpath)
        subdir_list.append(subdir)
        _remove_file(fpath)

    #
    # If any subdirs are empty, then remove them
    #
    for subdir in subdir_list:
        _remove_dir_if_empty(subdir)


def _remove_file(fpath: str):
    """
    Remove file - log any problems
    """
    if not fpath:
        return

    if not os.path.exists(fpath):
        return

    try:
        os.unlink(fpath)
    except OSError:
        Msg.warn(f'Error deleting file: {fpath}')


def _remove_dir_if_empty(dpath: str):
    """
    Remove directory (must be empty) - log any problems
    """
    if not dpath:
        return

    if not os.path.isdir(dpath):
        return

    (fls, dirs, lnks) = dir_list(dpath)

    if fls or dirs or lnks:
        return

    try:
        os.rmdir(dpath)
    except OSError:
        Msg.warn(f'Error deleting directory: {dpath}')


def _subdirs_with_file(topdir: str, targ_file: str) -> list[str]:
    """
    Given a directory,  find all subdirs which contain filename.

    i.e.
    Find all <x> for which the file:
        topdir/<x>/filename
    exists.

    Return list of <x>
    """
    matches: list[str] = []
    (_fls, dirs_all, _lnks) = dir_list(topdir, which='path')

    for subdir in dirs_all:
        (files, _dirs, _lnks) = dir_list(subdir, which='name')
        if targ_file in files:
            subdir_name = os.path.basename(subdir)
            matches.append(subdir_name)

    return matches


def _make_remove_list(num_keep: int, candidates: list[str]) -> list[str]:
    """
    Given list of paths of candidates, return
    list of those to be removed.
    """
    remove_list: list[str] = []
    if not candidates or len(candidates) < num_keep:
        return remove_list

    #
    # Sort list by file time - newest first
    # And make the list to remove
    #
    candidates.sort(key=os.path.getmtime, reverse=True)
    remove_list = candidates[num_keep:]
    return remove_list
