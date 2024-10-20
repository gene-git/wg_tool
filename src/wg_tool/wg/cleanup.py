# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
cleaner
"""
import os
import shutil
from lib import dir_list

def _cleaner(wgtool, num_keep, topdir, ind):
    """
    Clean topdir/db/xxx
      - delete all but the newest 'num_keep'.
      - should not be any files/symlinks in dir/db
      - directory topdir usually has symlinks into 'db/xxx/xxx'
        - make sure any symlinks pointing to db/xxx/xxx are retained
    """
    # pylint: disable=R0914

    vmsg = wgtool.vmsg
    wmsg = wgtool.wmsg

    ind1 = ind * " "
    ind2 = 2*ind * " "
    top_basename = os.path.basename(topdir)
    vmsg(f'{ind1} {top_basename}/')

    #
    # build sorted list - newest to oldest
    #
    dbdir = os.path.join(topdir, 'db')
    [flist, rm_list, llist] = dir_list(dbdir, which='path')

    if len(rm_list) <= num_keep:
        return

    # sort newest first
    rm_list.sort(key=os.path.getmtime, reverse=True)

    #
    # Warn if find anything other than the (datetime) dirs we expect
    #
    non_dirs = flist + llist
    if non_dirs:
        wmsg(f'Warn cleanup : non-directory files spotted {dbdir}')
        for item in non_dirs:
            vmsg(f'    {item}')

    #
    # Create list of dirs to keep from any link targets pointing into db_dir
    #
    [_flist, _dlist, llist] = dir_list(topdir, which='path')
    keep_dirs = []
    for item in llist:
        link_targ = os.readlink(item)
        link_targ_dir = os.path.dirname(link_targ)
        if link_targ_dir not in keep_dirs :
            # everything is viewed with topdir/xx
            top_targ_dir = os.path.join(topdir, link_targ_dir)
            keep_dirs.append(top_targ_dir)

    #
    # update remove list stripped of keepers
    # This will stay in sorted order
    #
    rm_list_final = []
    for item in rm_list:
        if item not in keep_dirs:
            rm_list_final.append(item)

    if len(rm_list_final) <= num_keep:
        return

    rm_list_final = rm_list_final[num_keep:]

    #
    # Ready to delete
    #
    for item in rm_list_final:
        db_date = os.path.join('db',os.path.basename(item)) + '/'
        vmsg(f'{ind2} {db_date}')
        shutil.rmtree(item)

def cleanup(wgtool):
    """
    Clean older configs and wg_configs
    """
    vmsg = wgtool.vmsg
    num_keep = wgtool.opts.keep_hist
    num_keep_wg = wgtool.opts.keep_hist_wg

    # ------------------------
    # configs
    #
    vmsg(f'\nCleanup - keep_conf={num_keep} keep_wg_conf={num_keep_wg}')
    lev1_dir = wgtool.conf_serv_dir
    lev1_dn = os.path.dirname(lev1_dir)
    vmsg(f'{"":>5s} {lev1_dn}/')
    _cleaner(wgtool, num_keep, lev1_dir, 10)

    first_pass = True
    for user_name in wgtool.users_all:
        lev2_dir = os.path.join(wgtool.conf_user_dir, user_name)
        if first_pass:
            lev2_bn = os.path.basename(wgtool.conf_user_dir)
            vmsg(f'{"":>10s} {lev2_bn}/')
            first_pass = False
        _cleaner(wgtool, num_keep, lev2_dir, 15)

    # ------------------------
    # wg configs
    #
    #vmsg('\nCleanup wg')
    tdir = wgtool.wg_serv_dir
    tdirname = os.path.dirname(tdir)
    vmsg(f'{"":>5s} {tdirname}/')
    _cleaner(wgtool, num_keep_wg, tdir, 10)

    # users
    first_pass = True
    for user_name in wgtool.users_all:
        user_dir = os.path.join(wgtool.wg_users_dir, user_name)
        if first_pass:
            tdirname = os.path.basename(wgtool.wg_users_dir)
            vmsg(f'{"":>10s} {tdirname}')
            first_pass = False
        _cleaner(wgtool, num_keep_wg, user_dir, 10)
