# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Project wg_tool
"""
__version__ = "8.0rc2"
__date__ = "2025-09-16"
__reldev__ = "release"


def version() -> str:
    """ report version and release date """
    vers = f'wg-tool: version {__version__} ({__reldev__}, {__date__})'
    return vers
