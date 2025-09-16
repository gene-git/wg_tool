# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
save/restore some command line options
  - support function for WgtOptBase
"""
from typing import (Any)
import os

from utils import Msg
from utils import make_dir_path
from utils import dict_to_toml_string
from utils import read_toml_file
from utils import write_path_atomic

from data import restrict_file_mode


def write_saved_options(opts: dict[str, Any], fpath: str) -> bool:
    """
    save options in TOML format:
      - keep_hist
      - keep_hist_wg

    Returns:
        bool:
        Success or fail.
    """
    if not fpath:
        return False

    save_dir = os.path.dirname(fpath)
    if not make_dir_path(save_dir):
        Msg.err(f'Save Options: Error creating {save_dir}\n')
        return False

    opts_save: dict[str, Any] = {}

    keys = ('hist', 'hist_wg')  # , 'net_compact')
    for key in keys:
        if opts.get(key) is not None:
            opts_save[key] = opts.get(key)

    if not opts_save:
        return True

    #
    # write it out (we dont need history files here)
    #
    opts_str = dict_to_toml_string(opts_save)
    fmode = restrict_file_mode()
    if not write_path_atomic(opts_str, fpath, fmode):
        Msg.err(f'Error saveing options file: {fpath}\n')
        return False

    return True


def read_saved_options(fpath: str) -> dict[str, Any]:
    """
    read saved options file and return a dictionary.
    """
    #
    # Allow more general values than str/int
    #
    opts_dict: dict[str, Any] = {}

    if not (fpath and os.path.isfile(fpath)):
        return opts_dict

    from_file = read_toml_file(fpath)

    #
    # backward compat: change older option names to current ones.
    #
    for (k, v) in from_file.items():
        if k == 'keep_hist':
            k = 'hist'
        elif k == 'keep_hist_wg':
            k = 'hist_wg'
        opts_dict[k] = v

    return opts_dict
