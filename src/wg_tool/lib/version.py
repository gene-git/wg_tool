# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Project wg_tool
"""
from .msg import info_msg

__version__ = "6.4.0"
__date__ = "2024-01-19"
__githash__ = "a6160b4c98"

def version() -> None:
    """ report version and release date """
    vers = f'wg-tool: version {__version__} ({__date__} commit {__githash__})'
    info_msg(f'{vers}')
