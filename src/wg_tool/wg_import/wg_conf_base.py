# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Data for a wireguard peer config
"""
# pylint: disable = invalid-name
# pylint: disable = too-few-public-methods
# pylint: disable = too-many-instance-attributes

from ids import Identity
from utils.debug import pprint


class WgConfPeer:
    """
    Peer Section of wireguard peer config
    """
    def __init__(self):

        self.PublicKey: str = ''
        self.PresharedKey: str = ''
        self.Endpoint: str = ''
        self.AllowedIPs: list[str] = []
        self.PersistentKeepalive: int = 0

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)


class WgConfInterface:
    """
    Interface section of wireguard peer config
    """
    def __init__(self):
        self.PrivateKey: str = ''
        self.Address: list[str] = []
        self.ListenPort: str = ''
        self.PreUp: list[str] = []
        self.PreDown: list[str] = []
        self.PostUp: list[str] = []
        self.PostDown: list[str] = []
        self.DNS: list[str] = []
        self.MTU: str = ''
        self.pubkey: str = ''

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)


class WgDns:
    """
    Gathered DNS info from each peer
    """
    def __init__(self):
        #
        # [Interface] section exposes DNS used by each peer.
        # - gather them up so pass 2 can determine if any common to all peers.
        # - Can share common hosts in vpninfo
        #   we leave any gateway DNS alone
        # - save each as : {host: count}
        #
        self.num_gw: int = 0
        self.num_cl: int = 0
        self.dns: dict[str, int] = {}


class WgConfBase:
    """
    One Wireguard peer config
        - each "peer" is a gateway (Endpoint)
          which will become a separate profile.
    """
    def __init__(self):

        self.file: str = ''
        self.ident: Identity = Identity()
        self.interface: WgConfInterface = WgConfInterface()
        self.peers: list[WgConfPeer] = []

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)
