# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Data for a wireguard peer config
"""
# pylint: disable = too-few-public-methods
from utils.debug import pprint
from peers import Profile


class GwInfo:
    """
    info about 1 gateway
    psk lists the id and psk of each peer
    psks {tag: psk}
    """
    def __init__(self):
        self.pubkey: str = ''
        self.prof: Profile
        self.endpoint: str = ''
        self.nets_wanted: list[str] = []
        self.nets_offered: list[str] = []
        self.vpn_nets: list[str] = []
        self.psks: dict[str, str] = {}

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)
