# SPDX-License-Identifier: MIT
# Copyright (c) 2022,2023 Gene C
"""
save/restore some command line options
  - support function for class WgtOptions
"""
import os
from .msg import err_msg
from .file_tools import make_dir_path
from .file_tools import open_file
from .toml import dict_to_toml_string
from .toml import read_toml_file

def _get_save_file(wgtopt):
    """ returns the path to save file """
    work_dir = wgtopt.work_dir
    save_dir = wgtopt.save_dir
    save_file = wgtopt.save_file

    if not save_dir or not save_file:
        return None

    if not work_dir:
        work_dir = './'

    save_dir_path = os.path.join(work_dir, save_dir)
    save_file_path = os.path.join(save_dir_path, save_file)
    return (save_dir_path, save_file_path)

def write_saved_opts(wgtopt):
    """
    save options:
      - keep_hist
      - keep_hist_wg
    """
    is_okay = True

    (save_dir_path, save_file_path) = _get_save_file(wgtopt)
    if not save_dir_path or not save_file_path:
        is_okay = False
        return is_okay

    is_okay = make_dir_path(save_dir_path)
    if not is_okay:
        err_msg(f'Save Options: Error creating {save_dir_path}')
        return is_okay

    opts_dict = {
            'keep_hist'     : wgtopt.keep_hist,
            'keep_hist_wg'  : wgtopt.keep_hist_wg,
            }
    opts_str = dict_to_toml_string(opts_dict)

    fobj = open_file(save_file_path, 'w')
    if fobj:
        fobj.write(opts_str)
        fobj.close()
    else:
        err_msg(f'Error saveing options file : {save_file_path}')
        is_okay = False

    return is_okay

def _set_value(wgtopt, opts_dict, key):
    """
    Sets the option key
     - command line (already set wgtopt.key)
     - save file
     - default
    """
    if getattr(wgtopt, key):
        return

    if opts_dict:
        value = opts_dict.get(key)
        if value:
            setattr(wgtopt, key, value)
            return

    def_key = f'default_{key}'
    value = getattr(wgtopt, def_key)
    setattr(wgtopt, key, value)

def read_merge_saved_opts(wgtopt):
    """
    read and merge saved options, priority:
       - cli (attribute set by caller)
       - saved (from file)
       - default (from default_xxx)
    """
    opts_dict = None

    (_save_dir_path, save_file_path) = _get_save_file(wgtopt)
    if not save_file_path:
        return

    opts_dict = read_toml_file(save_file_path)

    _set_value(wgtopt, opts_dict, 'keep_hist')
    _set_value(wgtopt, opts_dict, 'keep_hist_wg')
