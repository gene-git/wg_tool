# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Client Interface/Peer
"""
from typing import Any


def drop_lowercase_keys(dic: dict[str, Any]) -> dict[str, Any]:
    """
    Return dictionary with lower case keys removed
    """
    clean: dict[str, Any] = {}
    if not dic:
        return clean

    for (key, val) in dic.items():
        if not key.islower():
            clean[key] = val
    return clean


def list_are_same(l1: list[str], l2: list[str]) -> bool:
    """
    Return True if lists are same
    """
    # pylint: disable=too-many-return-statements
    if not l1:
        if not l2:
            return True
        return False

    if not l2:
        return False

    len_1 = len(l1)
    if len_1 != len(l2):
        return False

    if len_1 == 1 and l1 != l2:
        return False

    if sorted(l1) != sorted(l2):
        return False

    return True
