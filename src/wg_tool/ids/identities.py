# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2025-present  Gene C <arch@sapience.com>
"""
Unique Id Manager
Currently we are only using the hash part.
May or may not use the unique id part.
Name space by conbstruction is unique
"""

from .identity import Identity
from .parse_ids import parse_ids


class Identities:
    """
    List of Identities
    as passed on the command line
    """
    def __init__(self):
        self.ids: list[Identity] = []

    def vpn_names(self) -> list[str]:
        """
        Return list of unique vpn names
        """
        if not self.ids:
            return []

        names: set[str] = set()
        for one in self.ids:
            if one.vpn_name:
                names.add(one.vpn_name)
        return list(names)

    def acct_names(self, vpn_name: str) -> list[str]:
        """
        Return list of account names for this vpn
        """
        if not self.ids:
            return []

        names: set[str] = set()
        for one in self.ids:
            if one.vpn_name and one.vpn_name == vpn_name:
                if one.acct_name:
                    names.add(one.acct_name)
        return list(names)

    def prof_names(self, vpn_name: str, acct_name: str) -> list[str]:
        """
        Return list of profile names for this vpn.account
        """
        if not self.ids:
            return []

        if not vpn_name or not acct_name:
            return []

        names: set[str] = set()
        for one in self.ids:
            if (one.vpn_name == vpn_name
                    and one.acct_name
                    and one.acct_name == acct_name):
                if one.prof_name:
                    names.add(one.prof_name)
        return list(names)

    def parse_ids(self, names: list[str]) -> bool:
        """
        Initialize from the list of command line names
        """
        (ok, ids) = parse_ids(names)
        if not ok:
            return False
        self.ids = ids
        return True

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself
        """
        for identity in self.ids:
            identity.pprint(recurs=recurs)
