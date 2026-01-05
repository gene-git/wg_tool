# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
Read file (yaml or toml) and return dictionary of content.
"""
import os
from typing import Any

from wg_tool.utils import read_toml_file
from wg_tool.utils import read_yaml_file


def read_dict(fpath: str) -> dict[str, Any]:
    """
    Read a file and return dictionary.
    File can be yaml (preferred) or toml.
    """
    data: dict[str, Any] = {}
    if not fpath or not os.path.isfile(fpath):
        return data
    #
    # Try YAML first
    #
    data = read_yaml_file(fpath)
    if data and isinstance(data, dict):
        return data

    #
    # Fallback to TOML
    #
    data = read_toml_file(fpath)

    return data
