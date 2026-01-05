# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
Config file helper functions
- yaml handles None values as "null"
- toml does not can keep or strip from dictionary
"""
from typing import (Any)
from copy import deepcopy


def dict_none_to_empty(dic: dict[str, Any]) -> dict[str, Any]:
    """
    Replaces None values with empty string ''
    returns copy of dictionary
    """
    clean: dict[str, Any] = {}
    if not dic:
        return clean

    clean = deepcopy(dic)
    for (key, val) in clean.items():
        if val is None:
            clean[key] = ''
        elif isinstance(val, dict):
            clean[key] = dict_none_to_empty(val)
    return clean


def dict_remove_none(dic: dict[str, Any]) -> dict[str, Any]:
    """
    Rmoves keys with None values
    returns copy of dictionary
    """
    clean: dict[str, Any] = {}
    if not dic:
        return clean

    for (key, val) in dic.items():
        if val is not None:
            if isinstance(val, dict):
                new_val = dict_remove_none(val)
                if new_val:
                    clean[key] = new_val
            else:
                clean[key] = val
    return clean
