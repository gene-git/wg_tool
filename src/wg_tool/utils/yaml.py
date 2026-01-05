# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
yaml helper functions
- yaml handles None values as "null"
- we can keep or strip from dictionary
"""
# pylint: disable=duplicate-code
from typing import (Any)
import yaml

from .msg import Msg

from .read_write import write_path_atomic
from .read_write import read_file_path
from .file_tidy import dict_remove_none


def dict_to_yaml_string(dic: dict[str, Any],
                        flow_style: bool = False,
                        drop_empty: bool = False
                        ) -> str:
    """
    Returns a yaml formatted string from a dictionary
      - drop_empty: Keys with None values are removed/ignored
    """
    clean_dict = dic.copy()
    if drop_empty:
        clean_dict = dict_remove_none(dic)

    txt = yaml.dump(clean_dict, default_flow_style=flow_style)

    return txt


def read_yaml_file(fpath: str) -> dict[str, Any]:
    """
    read yaml file and return a dictionary
    """
    this_dict: dict[str, Any] = {}
    data: str = ''
    data = read_file_path(fpath)
    if data:
        try:
            this_dict = yaml.safe_load(data)
        except yaml.YAMLError as exc:
            Msg.err(f'File format error {exc}\n', level=1)
    return this_dict


def write_yaml_file(dic: dict[str, Any], fpath: str, flow_style: bool = False
                    ) -> bool:
    """
    write yaml file and return success/fail
    flow style defaults to block
    """
    okay = True
    if not dic or not fpath:
        return okay

    txt = dict_to_yaml_string(dic, flow_style=flow_style)

    if txt and not write_path_atomic(txt, fpath):
        okay = False
    return okay
