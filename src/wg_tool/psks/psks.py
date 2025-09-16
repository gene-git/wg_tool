# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Pre Shared Keys
"""
import os

from utils import Msg
from utils import read_toml_file
from utils.debug import pprint
from crypto import gen_psk

from data import get_vpnpsk_file
from data import write_dict


class Psks:
    """
    Manage pre shared keys (PSKs).
    Each pair of profiles, where at least 1 profile is a gatwway
    share one psk.

    For each psk they index key compresses a pair of profile ID tags
    """
    def __init__(self):
        self.psk: dict[str, str] = {}

    def to_dict(self) -> dict[str, str]:
        """
        Return dictionary of self
        """
        attribs = vars(self).copy()
        return attribs

    def from_dict(self, attribs: dict[str, str]):
        """
        Populate from dictionary
        """
        for (k, v) in attribs.items():
            setattr(self, k, v)

    def name_from_tags(self, tag1: str, tag2: str) -> str:
        """
        Make key from tag pair
        """
        if not (tag1 and tag2):
            Msg.warn('psks: missing tag\n')
            return ''

        # order tags so psk[t1, t2] = psk[t2, t1]
        if tag1 > tag2:
            pair = (tag1, tag2)
        else:
            pair = (tag2, tag1)

        name = pair[0] + '+' + pair[1]
        return name

    def lookup_psk(self, tag1: str, tag2: str) -> str:
        """
        Return the shared key for the tag pair
        PSK will be generated for this tag pair if not found
        unless no_psk is set True.

        Legacy no_psk:
        If no_psk is True then this tag pair will not have a PSK
        Some legacy clients may not have shared a PSK for this tag pair.
        This allows us to support those legacy older configs.
        """
        pair_name = self.name_from_tags(tag1, tag2)
        if not pair_name:
            return ''

        psk = self.psk.get(pair_name)
        if not psk:
            psk = ''
        return psk

    def get_set_shared_key(self, tag1: str, tag2: str, no_psk: bool = False
                           ) -> str:
        """
        Return the shared key for the tag pair
        PSK will be generated for this tag pair if not found
        unless no_psk is set True.

        Legacy no_psk:
        If no_psk is True then this tag pair will not have a PSK
        Some legacy clients may not have shared a PSK for this tag pair.
        This allows us to support those legacy older configs.
        """
        pair_name = self.name_from_tags(tag1, tag2)
        if not pair_name:
            return ''

        psk = self.psk.get(pair_name)
        if not psk:
            if no_psk:
                psk = ''
            else:
                psk = gen_psk()
            self.psk[pair_name] = psk

        return psk

    def put_shared_key(self, tag1: str, tag2: str, psk: str):
        """
        Install psk for the tag pair
        """
        pair_name = self.name_from_tags(tag1, tag2)
        self.psk[pair_name] = psk

    def clean_unknown_tags(self, gw_tags: list[str], tags: list[str]):
        """
        Clean any unknown tags from our psk list.
        Shouldn't be needed unless a profile is manually deleted.
        Tag pairs are between every gw and every other tag
        We never remove a profile, only mark it inactive of not needed.
        Could happen on partial migrations which failed in middle too.
        """
        known_names: list[str] = []
        for gw_tag in gw_tags:
            for tag in tags:
                if tag == gw_tag:
                    continue
                name = self.name_from_tags(gw_tag, tag)
                known_names.append(name)

        # drop any unknown
        names = list(self.psk.keys())
        for name in names:
            if name not in known_names:
                Msg.warn(f'Dropping unknown tag pair: {name}\n')
                del self.psk[name]

    def read_file(self, work_dir: str, vpn_name: str) -> bool:
        """
        Read psks from file.
        Since there may be no psks its not an error if missing.
        """
        psk_file = get_vpnpsk_file(work_dir, vpn_name)
        if not psk_file:
            return True

        psk_dict = read_toml_file(psk_file)
        if psk_dict and isinstance(psk_dict, dict):
            self.from_dict(psk_dict)
        return True

    def write_file(self, work_dir: str, vpn_name: str, footer: str) -> bool:
        """
        Save the PSKs
        Footer provides comments of psk -> ID-1 x ID-2
        For human consumption only.
        """
        psks_dict = self.to_dict()
        title = f'{vpn_name} PSKs'
        psk_file = get_vpnpsk_file(work_dir, vpn_name)
        file = os.path.basename(psk_file)
        (ok, changed) = write_dict(title, psks_dict, psk_file, footer=footer)
        if not ok:
            Msg.err('vpn psks: Error saving psk file {file}\n')
            return False
        if changed:
            file = os.path.basename(psk_file)
            Msg.info(f'  {file} updated\n')
        return True

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)
