# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
legacy user profile class
"""
# pylint: disable=invalid-name, too-many-instance-attributes
# pylint: disable=duplicate-code, too-few-public-methods
from data import mod_time_now
from utils import csv_string_to_list


class UserProfile:
    """
    Users can have 1 or more profiles.
    Each has separate access (phone, laptop etc)
    """
    def __init__(self, _prof_name, prof_dict):
        self.Address: list[str] = []
        self.PrivateKey: str = ''
        self.PublicKey: str = ''
        self.PresharedKey: str = ''
        self.AllowedIPs: list[str] = []
        self.Endpoint: str = ''
        self.DnsLinux = False
        self.PersistentKeepalive = 0

        self._changed = False

        for key, val in prof_dict.items():

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

        self.mod_time = mod_time_now()

    def __getattr__(self, name):
        return None
