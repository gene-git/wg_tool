# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
toml helper functions
    - NB toml write cannot handle None values
"""
from typing import (Any)
import os
from copy import deepcopy
import tomllib as toml
import tomli_w

from .read_write import (open_file, write_path_atomic)
from .msg import Msg


def _dict_none_to_empty(dic: dict[str, Any]) -> dict[str, Any]:
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
            clean[key] = _dict_none_to_empty(val)
    return clean


def _dict_remove_none(dic: dict[str, Any]) -> dict[str, Any]:
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
                new_val = _dict_remove_none(val)
                if new_val:
                    clean[key] = new_val
            else:
                clean[key] = val
    return clean


def dict_to_toml_string(dic: dict[str, Any], drop_empty: bool = False) -> str:
    """
    Returns a toml formatted string from a dictionary
      - Keys with None values are removed/ignored
    """
    clean_dict = dic
    if drop_empty:
        clean_dict = _dict_remove_none(dic)
    txt = tomli_w.dumps(clean_dict)
    return txt


def read_toml_file(fpath: str) -> dict[str, Any]:
    """
    read toml file and return a dictionary
    """
    this_dict: dict[str, Any] = {}
    data: str = ''
    if os.path.exists(fpath):
        fobj = open_file(fpath, 'r')
        if fobj:
            data = fobj.read()
            fobj.close()
        if data:
            try:
                this_dict = toml.loads(data)
            except toml.TOMLDecodeError as exc:
                Msg.err(f'File format error {exc}\n')
    return this_dict


def write_toml_file(dic: dict[str, Any], fpath: str) -> bool:
    """
    write toml file and return a success/fail
    """
    okay = True
    if not dic or not fpath:
        return okay

    txt = dict_to_toml_string(dic)
    if txt:
        if not write_path_atomic(txt, fpath):
            okay = False
    return okay
