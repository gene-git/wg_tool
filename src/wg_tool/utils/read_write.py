# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
File tools
"""
# pylint: disable=too-many-branches
from typing import (IO)
import os
import stat

from .msg import (Msg)
from .file_tools import make_dir_path
from .file_tools import os_rename


def open_file(path: str, mode: str) -> IO | None:
    """
    Open a file and return file object
    """
    # pylint: disable=unspecified-encoding, consider-using-with
    try:
        fobj = open(path, mode)
    except OSError as err:
        fobj = None
        Msg.err(f'Error opening file {path} : {err}')
    return fobj


def write_file(data: str, targ_dir: str, file: str) -> bool:
    """
    Write out text file
    """
    if not targ_dir:
        return False

    fpath = os.path.join(targ_dir, file)
    okay = write_path_atomic(data, fpath)
    if not okay:
        Msg.err(f'Failed to write {fpath}')
        return False
    return True


def write_path_atomic(data: str | list[str],
                      fpath: str,
                      fmode: int = -1,
                      dmode: int = -1,
                      save_prev: bool = False
                      ) -> bool:
    """
    Write data to fpath - atomic version.

    Args:
        data (str | list[str]):
            The data to write to file 'fpath'

        fmode (int):
            If positive number then file has chmod(fmode) applied to it.
            defaults to (rw-r----)
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP.

        dmode (int):
            If positive number then any directories that are created
            has chmod(dmode) applied to it.
            defaults to (rwxr-x--):
                stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP

        save_prev (bool):
            If true then if fpath exists it will be moved
            to Prev/xxx

    Return:
        bool:
            Success or fail.
    """
    #
    # Error if no data to write
    #
    if not data:
        Msg.err('write_path_atomic: no data to write')
        return False

    #
    # Create dest directories if needed
    #
    dirname = os.path.dirname(fpath)
    if dirname:
        if not make_dir_path(dirname, dmode):
            txt = f'Error making dest dirs {dirname}'
            Msg.err(f'write_path_atomic: {txt}')
            return False

    #
    # write temp file in same dir.
    #
    fpath_tmp = fpath + '.tmp'
    fob = open_file(fpath_tmp, "w")
    if not fob:
        return False

    if isinstance(data, list):
        for item in data:
            fob.write(item)
    else:
        fob.write(data)

    fob.flush()
    fd = fob.fileno()
    os.fsync(fd)

    #
    # Set any requested permissions
    #
    if fmode < 0:
        fmode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP

    if fmode > 0:
        try:
            os.chmod(fd, fmode)

        except OSError as err:
            Msg.warn(f' Warning chmod {fpath}: {err}')

    fob.close()

    #
    # Save any existing to dirname/Prev if requested
    #
    if save_prev and os.path.exists(fpath):
        Msg.plainverb(f'write_path_atomic saving {fpath} to Prev\n')
        save_dir = os.path.join(dirname, 'Prev')
        if make_dir_path(save_dir, dmode):
            filename = os.path.basename(fpath)
            saved_path = os.path.join(save_dir, filename)
            os_rename(fpath, saved_path)
        else:
            txt = f'Error making save dir {save_dir}'
            Msg.err(f'write_path_atomic: {txt}')
    #
    # rename to real file
    #
    if not os_rename(fpath_tmp, fpath):
        Msg.err(f'write_path_atomic rename error: {fpath_tmp}')
        return False
    return True


def copy_file_atomic(src: str, dst: str) -> bool:
    """
    Copy local file from src to dst
    """
    if not os.path.exists(src):
        return True

    fob = open_file(src, "r")
    if not fob:
        return False

    data = fob.read()
    fob.close()
    try:
        src_stat = os.stat(src)
    except OSError:
        # stat failed
        src_stat = None

    okay = write_path_atomic(data, dst)
    if not okay:
        return False

    # Set file time to match src
    if src_stat:
        os.utime(dst, ns=(src_stat.st_atime_ns, src_stat.st_mtime_ns))
    return True


def read_file(targ_dir: str, file: str) -> str:
    """ read text file """

    if not targ_dir:
        return ''

    fpath = os.path.join(targ_dir, file)
    try:
        fobj = open_file(fpath, 'r')
        if not fobj:
            Msg.err(f'Failed to read {fpath}')
            return ''
        data = fobj.read()
        return data

    except OSError as err:
        Msg.err(f'Error with file {fpath} : {err}')
        return ''
    return ''


def copy_file(src_dir: str, file: str, targ_dir: str) -> bool:
    """
    Copy file from src_dir to targ_dir
     return True on success
    """
    spath = os.path.join(src_dir, file)
    tpath = os.path.join(targ_dir, file)
    return copy_file_atomic(spath, tpath)


def write_pem(pem: bytes, db_dir: str, file: str) -> bool:
    """
    write pem byte string to file
     - pem is bytes => decode to string
    """
    if pem:
        pem_str = pem.decode('utf-8')
        is_okay = write_file(pem_str, db_dir, file)
    else:
        is_okay = False
    return is_okay


def read_pem(db_dir: str, pem_file: str) -> bytes:
    """
    read pem file and return PEM byte string
    """
    pem = b''
    pem_str = read_file(db_dir, pem_file)
    if pem_str:
        # pem = bytes(pem_str, 'utf-8')
        pem = pem_str.encode('utf-8')
    return pem
