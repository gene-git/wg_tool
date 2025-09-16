# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Format we use for modification times
"""
import os
from datetime import datetime


def _fmt():
    """ strftime format """
    fmt = '%y%m%d-%H%M%S'
    return fmt


def mod_time_now() -> str:
    """
    Mod time from current date time
    """
    fmt = _fmt()
    today = datetime.today()
    mod_time = today.strftime(fmt)
    return mod_time


def mod_time_file(file: str) -> str:
    """
    Mod time from file modification time
    """
    fmt = _fmt()
    mtime = os.path.getmtime(file)
    ftime = datetime.fromtimestamp(mtime)
    mod_time = ftime.strftime(fmt)
    return mod_time
