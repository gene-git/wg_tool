# SPDX-License-Identifier: MIT
# Copyright (c) 2022,2023 Gene C
"""
 wg-tool : save configs
"""
# pylint: disable=C0301
import os

from .file_tools import file_symlink
from .file_tools import format_file_header
from .file_tools import write_conf_file
from .file_tools import setup_save_path
from .file_tools import save_prev_symlink

def _strip_private(dic):
    """
    remove any private attributes
      - we recurse on sub dictionaries
    """
    for key,value in dic.items():
        if key[0] == '_':
            dic[key] = None
        if isinstance(value, dict):
            _strip_private(value)
    return dic

def write_server_config(wgtool):
    """
    Write server config if changed
        serv_dir/
                server -> data/<date>/server
                data/<date>/server
        - set link to point to current file
    """
    okay = True
    msg = wgtool.msg
    vmsg = wgtool.vmsg
    emsg = wgtool.emsg

    if wgtool.server.get_changed() :
        serv_dir = wgtool.conf_serv_dir
        serv_file = wgtool.conf_serv_file

        (actual_file, link_name, link_targ) = setup_save_path(wgtool, serv_dir, serv_file,mkdirs=True)
        msg(f'{"config":>10s}:   updating - server')
        vmsg(f'                    {actual_file}')

        header = format_file_header('Server Config', wgtool.now)
        server_dict = wgtool.server.to_dict()
        server_dict = _strip_private(server_dict)

        okay = write_conf_file(header, server_dict, actual_file)
        if okay:
            save_prev_symlink(serv_dir, link_name)
            file_symlink(link_targ, link_name)
        else:
            emsg(f'Error writing server config {actual_file}')
    return okay

def write_user_configs(wgtool):
    """
    write out user configs
    """
    # pylint: disable=R0914
    okay = True
    msg = wgtool.msg
    vmsg = wgtool.vmsg
    emsg = wgtool.emsg

    user_dir = wgtool.conf_user_dir
    for user_name in wgtool.users_changed:
        user = wgtool.users[user_name]
        user_dict = user.to_dict()
        user_dict = _strip_private(user_dict)

        this_user_dir = os.path.join(user_dir, user_name)
        user_file = f'{user_name}.conf'
        (actual_file, link_name, link_targ) = setup_save_path(wgtool, this_user_dir, user_file,mkdirs=True)

        msg(f'{"config":>10s}:   updating - {user_name}')
        vmsg(f'                     {actual_file}')

        header = format_file_header(f'User Config: {user_name}', wgtool.now)
        user_okay = write_conf_file(header, user_dict, actual_file)
        if user_okay:
            # if not link save it
            save_prev_symlink(user_dir, link_name)
            file_symlink(link_targ, link_name)
        else:
            emsg(f'Error writing user config {actual_file}')
            okay = False
    return okay
