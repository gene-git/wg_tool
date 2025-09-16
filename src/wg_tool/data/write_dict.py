# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Write dictionary to file in our standard toml format with header
"""
from typing import (Any)

from utils import dict_to_toml_string
from utils import Msg

from .mod_time import mod_time_now
from .write_db_file import write_db_file
# from .perms import restrict_file_mode


def write_dict(title: str,
               data_dict: dict[str, Any],
               fpath: str,
               footer: str = '') -> tuple[bool, bool]:
    """
    Write dictionary to file in toml format.
    Add comment header to top of file
    File has permision set to u=rw,g=rw

    Uses atomic write so nothing changed on error.

    Returns:
        (status: bool, changed: bool)
            status is True if succeeded.
            changed is True if file was written (new/changed)
    """
    if not fpath:
        return (False, False)

    now = mod_time_now()

    data = f'#\n#\t{title}\n#\t{now}\n#\n'
    data_s = dict_to_toml_string(data_dict)
    data += data_s
    if footer:
        data += footer

    (ok, changed) = write_db_file(data, fpath)
    if not ok:
        Msg.err('Error writing dictionary')
        return (False, changed)
    return (True, changed)
