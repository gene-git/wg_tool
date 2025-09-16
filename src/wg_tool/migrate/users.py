# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Legacy Users class
Collection of users and their profiles
"""
# pylint: disable=too-few-public-methods
import os

from utils import (Msg, read_toml_file, dir_list)
from .user import User


class Users:
    """
    Manage all users
    """
    def __init__(self, work_dir: str):
        self.okay: bool = True
        self.changed: bool = False
        self.names: list[str] = []
        self.data: list[User] = []

        # load each user
        users_dir = os.path.join(work_dir, "configs", "users")
        (_fls, self.names, _lnks) = dir_list(users_dir, which='name')

        for name in self.names:
            user_dir = os.path.join(users_dir, name)
            user_file = os.path.join(user_dir, f'{name}.conf')

            # read in all the user config
            # includes each profile in it's own section.
            user_dict = read_toml_file(user_file)
            if not user_dict:
                Msg.err(f'Error reading user config: {user_file}\n')
                self.okay = False
                return

            user = User(name, user_dict)
            self.data.append(user)
