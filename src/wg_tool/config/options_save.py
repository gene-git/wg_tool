# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
save/restore some command line options
  - support function for class WgtOptions
"""
import os
from lib import err_msg
from lib import (make_dir_path, open_file)
from lib import (dict_to_toml_string, read_toml_file)

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
            'prefixlen_4'   : wgtopt.prefixlen_4,
            'prefixlen_6'   : wgtopt.prefixlen_6,
            'user_keepalive': wgtopt.user_keepalive,
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

    _set_value(wgtopt, opts_dict, 'prefixlen_4')
    _set_value(wgtopt, opts_dict, 'prefixlen_6')
