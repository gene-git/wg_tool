# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Project wg_tool
"""
__version__ = "7.4.0"
__date__ = "2025-03-08"
__reldev__ = "release"

def version() -> str:
    """ report version and release date """
    vers = f'wg-tool: version {__version__} ({__reldev__}, {__date__})'
    return vers
