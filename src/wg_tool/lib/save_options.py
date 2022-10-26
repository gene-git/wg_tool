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

def write_cli_opts(wgtopt):
    """
    save options:
      - keep_hist
      - keep_hist_wg
    """
    is_okay = True
    save_dir = wgtopt.save_dir
    save_file = wgtopt.save_file

    if not save_dir or not save_file:
        return is_okay

    is_okay = make_dir_path(save_dir)
    if not is_okay:
        err_msg(f'Save Options: Error creating {save_dir}')
        return is_okay

    opts_dict = {
            'keep_hist'     : wgtopt.keep_hist,
            'keep_hist_wg'  : wgtopt.keep_hist_wg,
            }
    opts_str = dict_to_toml_string(opts_dict)

    save_path = os.path.join(save_dir, save_file)
    fobj = open_file(save_path, 'w')
    if fobj:
        fobj.write(opts_str)
        fobj.close()
    else:
        err_msg(f'Error saveing options file : {save_path}')
        is_okay = False

    return is_okay

def read_cli_opts(wgtopt):
    """
    read saved options
       return as dictionary
    """
    opts_dict = None

    save_dir = wgtopt.save_dir
    save_file = wgtopt.save_file

    if not save_dir or not save_file:
        return

    save_path = os.path.join(save_dir, save_file)
    opts_dict = read_toml_file(save_path)

    if opts_dict:
        keep_hist = opts_dict.get('keep_hist')
        if keep_hist:
            wgtopt.keep_hist = keep_hist

        keep_hist_wg = opts_dict.get('keep_hist_wg')
        if keep_hist_wg:
            wgtopt.keep_hist_wg = keep_hist_wg
