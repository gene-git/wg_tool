# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Determine the ID string from wg config pathname
"""
import os
from pathlib import Path

from utils import Msg


def wg_conf_file_to_id(file: str) -> str:
    """
    fpath should be path taking form:

        /path/to/xxx/vpn_name/acct_name/prof_name.conf

    From this id_str = vpn_name.acct_name.prof_name
    If file does not exist then return empty string
    Note path must have at least 3 components.
    """
    id_str: str = ''
    if not file or not os.path.isfile(file):
        return id_str

    path = Path(file)
    parts = path.parts
    if len(parts) < 3:
        Msg.warn(f'Import file ({file}) needs to be vpn/acct/prof.conf\n')
        return ''

    prof = parts[-1]
    prof = prof.split('.conf')[0]
    acct = parts[-2]
    vpn = parts[-3]
    id_str = f'{vpn}.{acct}.{prof}'
    return id_str
