# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Legacy version < v 8.x
server data class
"""
# pylint: disable=invalid-name, too-many-instance-attributes
# pylint: disable=duplicate-code

from utils import (Msg, read_toml_file)
from utils import (csv_string_to_list)


class ServerData:
    """
    The db data
    """
    def __init__(self):
        self.active_users: list[str] = []
        self.Address: list[str] = []
        self.Hostname: str = ''
        self.Hostname_Int: str = ''
        self.ListenPort: str = ''
        self.ListenPort_Int: str = ''
        self.PrivateKey: str = ''
        self.PublicKey: str = ''
        self.PostUp: str = ''
        self.PostDown: str = ''
        self.DNS_SEARCH: list[str] = []
        self.DNS: list[str] = []
        self.mod_time: str = ''

    def load(self, db_path: str) -> bool:
        """
        Load the db file

        Returns: success/fail
        """
        data_dict = read_toml_file(db_path)

        if not data_dict:
            Msg.err(f'Error: Missing server db : {db_path}\n')
            return False

        self.from_dict(data_dict)

        return True

    def from_dict(self, data_dict: dict[str, str | list[str]]):
        """
        Load data fields from dictionary
          todo: add check key is known?
          use getattr() return None for unknown
        """
        for key, val in data_dict.items():

            if key == 'Address':
                if isinstance(val, list):
                    lval = val
                else:
                    lval = csv_string_to_list(val)
                setattr(self, key, lval)

            elif key == 'AllowedIPs':
                # new_key = 'nets_offered'
                if isinstance(val, list):
                    lval = val
                else:
                    lval = csv_string_to_list(val)
                setattr(self, key, lval)

            else:
                setattr(self, key, val)
