# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
File writer that keeps history
"""
import os
# import stat

from crypto import message_digest

from utils import Msg
from utils import open_file
from utils import make_dir_path
from utils import file_symlink
from utils import write_path_atomic
from utils import clean_comments

from .paths import get_db_name
from .mod_time import mod_time_now
from .perms import restrict_file_mode


def write_db_file(data: str,
                  fpath: str,
                  fmode: int = -1,
                  ok_comments: list[str] | None = None) -> tuple[bool, bool]:
    """
    Writes file to dated directory and makes a symlink to that.
    Write happens if file is changed or new.

    To compare content, comment lines are stripped out.
    Empty data is considered data and will be written if need be.

    Args:
        data (str):
            The file data to be written.

        fpath (str):
            The target file. If content without comments is
            new or differs from input data then it is written
            to db/<date> and fpath is made symlink to that file.
            i.e.
                if fpath is <topdir>/filename
                then
                <topdir>/filename -> <topdir>/db/<date>/filename
        fmode (int):
            file mode (stat.S_IRUSR etc) - defaults to restricted.

        ok_comments (list[str] | None):
            Data is compated to file content ignoring any comments
            except those in ok_comments. Default is all comments
            are ignored when comparing data vs file, to determine any
            change.

    Returns:
        tuple[status: bool: changed: bool]
            status is True if all okay.
            changed is True if file was written to disk (changed/new).
    """
    good_comments: list[str] = []
    if ok_comments is not None:
        good_comments = ok_comments

    same = _same_content(fpath, data, good_comments)
    if same:
        return (True, False)

    topdir = os.path.dirname(fpath)
    filename = os.path.basename(fpath)

    if not make_dir_path(topdir):
        Msg.err(f'Error making directory: {topdir}\n')
        return (False, False)

    db_name = get_db_name()
    db_topdir = os.path.join(topdir, db_name)
    if not make_dir_path(db_topdir):
        Msg.err(f'Error making directory: {db_topdir}\n')
        return (False, False)

    mod_time = mod_time_now()
    db_dir = os.path.join(db_topdir, mod_time)
    db_file = os.path.join(db_dir, filename)

    link_target = os.path.join(db_name, mod_time, filename)

    # write data
    # fmode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
    if fmode < 0:
        fmode = restrict_file_mode()

    if not write_path_atomic(data, db_file, fmode):
        Msg.err(f'Error writing {db_file}\n')
        return (False, False)

    # symlink
    if not file_symlink(link_target, fpath):
        Msg.err(f'Error making symlink : {fpath} -> {link_target}\n')
        return (False, False)
    return (True, True)


def _same_content(fpath: str, data: str, ok_comments: list[str]) -> bool:
    """
    Determins if fpath and data have some content
    """
    if not fpath or not os.path.exists(fpath):
        return False

    fob = open_file(fpath, 'r')
    if not fob:
        return False

    file_data = fob.read()
    fob.close()
    if not file_data:
        return False

    file_data = clean_comments(file_data, ok_comments=ok_comments)
    clean_data = clean_comments(data, ok_comments=ok_comments)

    if len(clean_data) != len(file_data):
        return False

    # check data is same
    file_data_hash = message_digest(file_data.encode('utf-8'))
    clean_data_hash = message_digest(clean_data.encode('utf-8'))

    if file_data_hash == clean_data_hash:
        return True

    return False
