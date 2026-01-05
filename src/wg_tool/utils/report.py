# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
Report
"""


def state_marker(hidden: bool, active: bool) -> str:
    """
    Return marker to use in reports for this state
    active: 🗸 + ☀️
    inactive: ✘ 🗙 - 😴
    hidden: 🛇 ! ♰
    """
    marker = '✘'
    if hidden:
        marker = '🛇'
    elif active:
        marker = '🗸'
    return marker
