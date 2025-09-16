# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Strip any non-public dictionary values.
"""
from typing import (Any)


def strip_private(dic: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively remove any private attributes (any with leading "_")

    While we can set value to None or delete the key/value pair,
    we cannot modify the dictionary in flight and it's also recursive.
    So we set val to None and caller handles None values appropriately.
    """
    for (key, value) in dic.items():
        if key[0] == '_':
            dic[key] = None

        if isinstance(value, dict):
            strip_private(value)
    return dic
