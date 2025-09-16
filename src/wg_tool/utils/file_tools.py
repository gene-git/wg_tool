# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
File related tools
"""
import os
import stat
import tempfile

from .msg import Msg


def save_prev_symlink(fdir: str, orig: str):
    """
    If link exists rename to orig.prev
    If not a link then move to unique subdir
        fdir/fname -> fdir/saved.xxx/fname
    """
    if os.path.exists(orig):
        if os.path.islink(orig):
            saved = f'{orig}.prev'
        else:
            save_dir = tempfile.mkdtemp(suffix='', prefix='Saved',
                                        dir=fdir)
            basefile = os.path.basename(orig)
            saved = os.path.join(save_dir, basefile)
        os.rename(orig, saved)


def os_unlink(fpath: str) -> bool:
    """
    Delete file if exists - no directories allowed.
    Returns True if succeeds
    """
    if not fpath or not os.path.isfile(fpath):
        return True

    try:
        os.unlink(fpath)
    except OSError as exc:
        Msg.plainverb(f'Failed to unlink file {fpath} : {exc}\n')
        return False

    return True


def os_rename(old_path: str, new_path: str) -> bool:
    """
    Rename a file - if new_path exists it is first removed
    new_path must either not exist or be file or an empty directory.
    """
    if not (old_path and new_path):
        return True

    #
    # Check if destination exists
    #
    if os.path.exists(new_path):
        if os.path.isdir(new_path):
            try:
                os.rmdir(new_path)
            except OSError as exc:
                Msg.err(f'os_rename error unlinking target {exc}\n')
                return False
        else:
            try:
                os.unlink(new_path)
            except OSError as exc:
                Msg.err(f'os_rename error unlinking target {exc}\n')
                return False
    try:
        os.rename(old_path, new_path)
    except OSError as exc:
        Msg.err(f'os_rename error renaming {exc}\n')
        return False
    return True


def file_symlink(target: str, linkname: str) -> bool:
    """
    file_symlink(target, linkname)
    Does equivalent to:  ln -s src dst
    Returns True when succeeds.
    """
    #
    # check if its there and correct
    # If there but wrong, remove the old link
    #
    done = False
    if os.path.islink(linkname):
        # existing is a link
        try:
            targ = os.readlink(linkname)
        except OSError:
            return False

        if targ == target:
            done = True
        else:
            try:
                os.unlink(linkname)
            except OSError:
                return False

    elif os.path.isfile(linkname):
        # existing is a file - remove it
        try:
            os.unlink(linkname)
        except OSError:
            return False

    if not done:
        try:
            os.symlink(target, linkname)
        except OSError:
            return False
    return True


def make_dir_path(path_dir: str, dirmode: int = -1) -> bool:
    """
    makes directory and any missing path components
      - set reasonable permissions
    """
    if dirmode < 0:
        dirmode = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP
    try:
        os.makedirs(path_dir, exist_ok=True)
        if dirmode > 0:
            os.chmod(path_dir, dirmode)
    except OSError:
        return False
    return True


def dir_list(indir: str, which: str = 'name'
             ) -> tuple[list[str], list[str], list[str]]:
    """
    Get a list of files in a local directory
    returns a list of files/dirs/links in a directory
    which - 'name' returns filename, 'path' returns the 'path'

    [flist, dlist, llist]
        flist = list of files
        dlist = list of dirs
        llist = list of links
    NB order care needed - symlinks are also files or dirs -
    so always check link before file or dir as we want links separated
    whether or not they point to a dir or file.
    """
    flist: list[str] = []
    dlist: list[str] = []
    llist: list[str] = []

    if not os.path.isdir(indir):
        return (flist, dlist, llist)

    scan = None
    try:
        scan = os.scandir(indir)
    except OSError:
        return (flist, dlist, llist)

    if not scan:
        return (flist, dlist, llist)

    for item in scan:
        file = item.name
        if which == 'path':
            file = item.path

        if item.is_symlink():
            llist.append(file)

        elif item.is_file():
            flist.append(file)

        elif item.is_dir():
            dlist.append(file)
    scan.close()

    return (flist, dlist, llist)


def os_chmod(path: str, perm: int) -> bool:
    """
    os.chmod with exception check
     - returns True/False if all okay/not okay
    """
    try:
        os.chmod(path, perm)
    except OSError:
        return False
    return True


def set_restrictive_file_perms_walk(topdir: str) -> bool:
    """
    Restrict permissions recursively
        user = rwX
        group = rX
        other =
     where X means x if a dir
     Return True unless any os.chmod() throws exception
    Note: This can be slow on NFS - however using scandir directly
          was even slower for some reason.
    """

    if not (os.path.exists(topdir) and os.path.isdir(topdir)):
        return False

    file_perm_x = stat.S_IRWXU | stat.S_IXGRP | stat.S_IRGRP
    file_perm = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
    dir_perm = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP

    okay = True

    is_ok = os_chmod(topdir, dir_perm)
    if not is_ok:
        okay = False

    for (root, dirs, files) in os.walk(topdir):
        # directories
        for this_dir in dirs:
            this_path = os.path.join(root, this_dir)
            if os.path.islink(this_path):
                continue

            is_ok = os_chmod(this_path, dir_perm)
            if not is_ok:
                okay = False

        # files
        for this_file in files:
            this_path = os.path.join(root, this_file)
            if os.path.islink(this_path):
                continue

            # keep existing executable
            perms = file_perm
            if os.access(this_path, os.X_OK):
                perms = file_perm_x
            is_ok = os_chmod(this_path, perms)
            if not is_ok:
                okay = False
    return okay


def set_restrictive_file_perms(topdir: str) -> bool:
    """
    This is slower than os.walk() on NFS
    Both are fast on non-NFS
    Restrict permissions recursively
        user = rwX
        group = rX
        other =
     where X means x if a dir
     Return True unless any os.chmod() throws exception
    """
    # pylint: disable=too-many-branches
    scan = None
    try:
        scan = os.scandir(topdir)
    except OSError:
        return True

    if not scan:
        return True

    # file -> rw-r---- (with ug+x for executables)
    #  dir -> rwxr-x---
    file_perm = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
    dir_perm = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP

    okay = True
    if not os_chmod(topdir, dir_perm):
        # Keep going so can do what we can.
        okay = False

    for item in scan:

        if item.is_symlink():
            continue

        fstat = item.stat()
        fmode = fstat.st_mode

        if item.is_file():
            #
            # Files:
            # - ug+x for executables
            #
            fperm = file_perm

            if fmode & stat.S_IXUSR:
                fperm |= stat.S_IXUSR

            if fmode & stat.S_IXGRP:
                fperm |= stat.S_IXGRP

            if fmode != fperm:
                if not os_chmod(item.path, fperm):
                    okay = False

        elif item.is_dir():
            #
            # Directories:
            #  set perms then recurse
            #
            fperm = dir_perm
            if fmode != fperm:
                if not os_chmod(item.path, dir_perm):
                    okay = False
            if not set_restrictive_file_perms(item.path):
                okay = False

    return okay
