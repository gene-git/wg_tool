# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Default file mode permissions
"""
import stat


def restrict_file_mode() -> int:
    """
    Limit file permissions to u=rw,g=r
    """
    perms = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP  # | stat.S_IWGRP
    return perms


def restrict_dir_mode() -> int:
    """
    Limit directory permissions to u=rwx,g=rx
    """
    perms = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP
    return perms
