# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2025-present  Gene C <arch@sapience.com>
"""
Unique Id Manager
Currently we are only using the hash part.
May or may not use the unique id part.
Name space by conbstruction is unique
"""
import uuid

from utils import Msg
from utils.debug import pprint
from data.constants import DB_DIR


class Identity:
    """
    Every peer has a unique ID composed of
    3 name elements:
        vpn_name, account_name, profile_name

    There is also a unique identifying tag.

    A "full" ID has all 3 name elements.
    The 3 tuple vpn.account.profile is unique.

    account names are unique to their parent vpn
    profile names are unique the parent account.

    Different vpn_names may contain the same account/profile name as
    other vpns. Similarly 2 accounts in the same vpn may use the same
    profile names as one another.

    This is desirable. e.g.
        vpn1:bob:laptop
        vpn1:sue:laptop

    id_str takes tht form:
        'vpn_name.acct_name.prof_name'

    tag is globally unique.
    """
    def __init__(self):
        self.id_str: str = ''
        self.vpn_name: str = ''
        self.acct_name: str = ''
        self.prof_name: str = ''
        self.tag: str = ''

    def from_str(self, id_str: str):
        """
        Parse id string : vpn:peer:prof to an ID tuple

        Parsing is left to right:
        e.g.
            a.b.c   -> vpn_name.acct_name.prof_name
            a.b     -> vpn_name.acct_name
            a       -> vpn_name
        """
        self.id_str = id_str
        self.vpn_name = ''
        self.acct_name = ''
        self.prof_name = ''

        if not id_str:
            return

        # allow / or .
        if '/' in id_str:
            id_str = id_str.replace('/', '.')

        parts = id_str.split('.', maxsplit=2)
        num_parts = len(parts)

        self.vpn_name = parts[0]
        if num_parts >= 3:
            self.acct_name = parts[1]
            self.prof_name = parts[2]

        elif num_parts >= 2:
            self.acct_name = parts[1]

        self.refresh()

    def to_dict(self) -> dict[str, str]:
        """
        Map self to a dictionary
        """
        attribs: dict[str, str] = vars(self).copy()
        return attribs

    def from_dict(self, attribs: dict[str, str]):
        """
        Map dictionary to attribs
        """
        for (k, v) in attribs.items():
            setattr(self, k, v)

    def new_tag(self):
        """
        Make a new tag
        """
        self.tag = generate_tag()

    def refresh(self) -> bool:
        """
        Ensure id_str generated from
        id_str(vpn, peer, prof)
        returns True if changed
        Needed since names can be changed directly
        without using a method provided by this class.
        """
        changed = False
        id_str = f'{self.vpn_name}.{self.acct_name}.{self.prof_name}'
        if id_str != self.id_str:
            self.id_str = id_str
            changed = True
        return changed

    def full(self) -> bool:
        """
        Returns true if all id components present
        """
        if self.vpn_name and self.acct_name and self.prof_name:
            return True
        return False

    def vpn_only(self) -> bool:
        """
        Returns true if all id components present
        """
        if self.vpn_name and not self.acct_name and not self.prof_name:
            return True
        return False

    def validate_names(self) -> bool:
        """
        Check the vpn/peer/prof are valid names
        """
        if self.vpn_name and not self.is_valid_name(self.vpn_name):
            Msg.err(f'Invalid name {self.vpn_name}\n')
            return False

        if self.acct_name and not self.is_valid_name(self.acct_name):
            Msg.err(f'Invalid name {self.acct_name}\n')
            return False

        if self.prof_name and not self.is_valid_name(self.acct_name):
            Msg.err(f'Invalid name {self.prof_name}\n')
            return False
        return True

    def set_vpn_name(self, vpn_name: str) -> bool:
        """
        Update the vpn_name
        Returns True if changed
        """
        if vpn_name != self.vpn_name:
            self.vpn_name = vpn_name
            self.refresh()
            return True
        return False

    def set_acct_name(self, acct_name: str) -> bool:
        """
        Update the acct_name
        Returns True if changed
        """
        if acct_name != self.acct_name:
            self.acct_name = acct_name
            self.refresh()
            return True
        return False

    def set_prof_name(self, prof_name: str) -> bool:
        """
        Update the prof_name
        Returns True if changed
        """
        if prof_name != self.prof_name:
            self.prof_name = prof_name
            self.refresh()
            return True
        return False

    @staticmethod
    def is_valid_name(name: str) -> bool:
        """
        Check name (vpn, peer or profile) is valid

        Valid are: alphanumeric or one of the valid list
                    '-=_.~+;@'
        """
        if not name:
            return False

        valids = ['-', '=', '_', ':', ',', '~', '+', ';']
        for char in list(name):
            if not (char.isalnum() or char in valids):
                return False

        if name.startswith('.'):
            return False

        if name == DB_DIR:
            return False
        return True

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)


def generate_tag() -> str:
    """
    Returns globally unqique tag
    """
    tag = str(uuid.uuid4())
    return tag

# def _make_id_hash(vpn_name: str, acct_name: str, prof_name: str) -> str:
#     """
#     Digest Hash of vpn:peer:prof
#     """
#     name = f'{vpn_name}:{acct_name}:{prof_name}'
#     digest = message_digest(name.encode('utf-8'))
#     digest_str = digest.hex()
#     return digest_str
