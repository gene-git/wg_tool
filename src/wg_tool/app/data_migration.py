# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
wg-tool primary class

Tool to administer wireguard vpns.
Each "vpn" has its own suite of peers. Some peers are clients
which connect to a gateway (which listens on a known ip/port)
"""
# pylint: disable=invalid-name, too-many-instance-attributes
# pylint: disable=too-many-return-statements, too-many-branches
import os

from config import Opts
from utils import Msg
from utils import dir_list

from data import get_top_dir
from migrate import migrate_data


def do_data_migration(opts: Opts) -> tuple[bool, bool]:
    """
    Check for legacy data and migrate if asked.
    Returns:
        (needed: bool, done: bool):
        Needed true if migrtion needed else false.
        Done is true if data was migrated now.
    """
    # Check if migrating older config
    if _check_migration_needed(opts):
        Msg.info('Legacy data migration needed:\n')
        if opts.migrate:
            migrate_data(opts)
            Msg.plain(' Data migrated\n')
            return (True, True)
        Msg.err(' Migration needed - ')
        Msg.plain('Please migrate to new format with --migrate option\n')
        return (True, False)

    if opts.migrate:
        Msg.warn('Migration not needed\n')
        return (False, True)
    return (False, True)


def _check_migration_needed(opts: Opts) -> bool:
    """
    Check if legacy and not new data.
    If so return True
    If have new data then no migration needed
    Returns True if data migration needed.
    Old server might have internal which we now count as 2.
    Ignore this case in our check here. Means if migration
    has these and it died on last one we will miss this case.
    It's good enough.
    """
    # check for new top dir
    topdir = get_top_dir(opts.work_dir)
    acct_dir = os.path.join(topdir, 'vpn1')
    num_accts = _dir_has_subdirs(acct_dir)

    #
    # legacy top dir
    #  - should have server, users
    #  - count users by num dirs
    #  - to count profiles we need to read each user profile
    #    and count dictionaries
    #
    db_dir = os.path.join(opts.work_dir, "configs")
    num_old_serv = 0
    num_old_users = 0

    serv_conf = os.path.join(db_dir, 'server', 'server.conf')
    if os.path.isfile(serv_conf):
        num_old_serv = 1

    users_dir = os.path.join(db_dir, 'users')
    num_old_users = _dir_has_subdirs(users_dir)

    num_old_accts = num_old_serv + num_old_users
    if num_old_accts == 0 or num_accts >= num_old_accts:
        return False

    if 0 < num_accts <= num_old_accts:
        Msg.warn('Possible incomplete migration?\n')
        Msg.warn('Please delete Data and Data-wg and redo -migraten\n')
        return True
    return True


def _dir_has_subdirs(adir: str) -> int:
    """
    Returns number of subdirs in directory
    Returns 0 if directory doesn't exist or has no subdirs
    """
    num_subdirs: int = 0
    if not os.path.isdir(adir):
        return num_subdirs

    (_files, dirs, _lnks) = dir_list(adir)

    if dirs:
        num_subdirs = len(dirs)
    return num_subdirs
