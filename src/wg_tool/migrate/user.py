# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Client Interface/Peer
"""
# pylint: disable=invalid-name,too-few-public-methods
from typing import Any

# from utils import Msg
from data import (mod_time_now)

from .user_profile import UserProfile


class User:
    """
    User Class:
      - active_configs : list
      - config : dictionary of each config (instance of WgtUserItem)
    """
    # pylint: disable=
    def __init__(self,
                 name: str,
                 user_dict: dict[str, Any]
                 ):  # , user_dict):
        self.name: str = name
        self.active_profiles: list[str] = []
        self.profile: dict[str, UserProfile] = {}

        self._changed = False

        key_map = {
                'PreUp': 'pre_up',
                'PreDown': 'pre_down',
                'PostUp': 'post_up',
                'PostDown': 'post_down',
                }

        for key, val in user_dict.items():
            if isinstance(val, dict):
                prof_name = key
                prof_dict = val
                self.profile[prof_name] = UserProfile(prof_name, prof_dict)
            elif key in list(key_map):
                mkey = key_map[key]
                setattr(self, mkey, val)
            else:
                setattr(self, key, val)
        self.mod_time: str = mod_time_now()

    def __getattr__(self, name):
        return None
