# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
 Read input configs
"""
import os
from .toml import read_toml_file
from .file_tools import os_scandir
from .utils import file_date_time_str

def read_server_config(wgtool):
    """
    Read server config into dictionary
    """
    conf_path = os.path.join(wgtool.conf_serv_dir, wgtool.conf_serv_file)
    conf = read_toml_file(conf_path)

    if conf and not conf.get("mod_time"):
        # use conf file mod time if older config
        conf["mod_time"] = file_date_time_str(conf_path)
        conf["_changed"] = True

    return conf

def _fix_profile_mod_times(user_conf, conf_file):
    """
    If user conf missing mod_time set it to mod time of conf gile
    If any profile missing mod_time, set it to user conf time
        - better than None
        - as things get updated this will updated
    """
    if not user_conf.get("mod_time"):
        user_conf["mod_time"] = file_date_time_str(conf_file)
        user_conf["_changed"] = True
    mod_time = user_conf["mod_time"]

    for _prof_name, prof in user_conf.items():
        if isinstance(prof, dict):
            if not prof.get("mod_time"):
                prof["mod_time"] = mod_time
                prof["_changed"] = True

def _read_one_user(wgtool, user_name, user_path, conf_dicts):
    """
    Scans for ".conf" files in this users dir
    Reads any found and append the dictionary to the
    list of conf_dicts
    """
    wmsg = wgtool.wmsg
    scan = os_scandir(user_path)
    if scan:
        for item in scan:
            if not item.is_file() and not item.is_symlink():
                continue
            if item.name.endswith('.conf'):
                conf = read_toml_file(item.path)
                if conf:
                    if not conf.get('name'):
                        conf['name'] = user_name

                    _fix_profile_mod_times(conf, item.path)

                    conf_dicts.append(conf)
                else:
                    wmsg(f'Failed to read user config : {item.path}')

def read_user_configs(wgtool):
    """
    Find and read all client configs
    Any file ending with '.conf' in the configs/users/<username>/*.conf
    """

    # There is one dir per user in "user_dir"
    user_dir = wgtool.conf_user_dir
    if not os.path.exists(user_dir) or not os.path.isdir(user_dir):
        return None

    #
    # get list of user configs and read them
    #
    conf_dicts = []
    top_dir_scan = os_scandir(user_dir)
    if top_dir_scan:
        for top_item in top_dir_scan:
            if top_item.is_dir():
                user_name = top_item.name
                _read_one_user(wgtool, user_name, top_item.path, conf_dicts)

    return conf_dicts
