# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Profile: data
"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods, invalid-name
from data import mod_time_now
from ids import Identity
from utils.debug import pprint


class ProfileBase:
    """
    Data part of Profile
    """
    def __init__(self):
        self.ident: Identity = Identity()

        #
        # Address is standard address (x.x.x.10/32)
        # AddressWg is in wireguard network format
        #   ip-w-host-bits/prefix (x.x.x.10/24)
        #
        self.Address: list[str] = []
        self.AddressWg: list[str] = []

        self.PrivateKey: str = ''
        self.PublicKey: str = ''

        #
        # Legacy flag to request no psk with each tag listed.
        # NB. Legacy client (user) only. Gateways must always
        # be able to share PSK.
        #
        self.no_psk_tags: list[str] = []

        self.PersistentKeepalive: int = 0
        self.MTU: str = ''

        self.pre_up: list[str] = []
        self.pre_down: list[str] = []
        self.post_up: list[str] = []
        self.post_down: list[str] = []

        #
        # AllowedIPs defauls to 0/0 unless changed by user
        # in which case we mark it allowed_ips_own
        # internal nets are any additional nets available via
        # this peer (can be gw or client)
        # internet_gw
        #   this gw offers internet access
        #   allowips = all (includes internal nets + internet)
        # which provides it (gw which has internet_gw) set.
        #
        # internet_offered
        #   - gateways only - gateway offers internet access
        #     to clients and will use NAT to do so.
        #   - adds 0/0, ::/0 - AllowedIPs = (allowed_nets + 0/0 + ::/0)
        #   - defaults to False
        #
        # internet_wanted
        #   - asking to have internet access provided by a gateway.
        #   - error if no gw offers internet access
        #
        # nets_wanted
        #   - list of networks provided by other peer(s)
        #
        # nets_offered
        #   - list of networks provided by this peer for other peer(s)
        #
        # self.nets: list[str] = []
        self.nets_offered: list[str] = []
        self.nets_wanted: list[str] = []
        self.internet_offered: bool = False
        self.internet_wanted: bool = True

        #
        # gateways
        #  - may have 1 or 2 Endpoints : host_or_ip:port
        # Endpoint_alt
        #   alternate endpoint (usualy internal)
        # Clients:
        #   use_alternate
        #       if true then this profile will generate an alternate
        #       config using alternate endpoint(s)
        #
        self.Endpoint: str = ''
        self.Endpoint_alt: str = ''
        self.alternate_wanted: bool = False

        self.use_vpn_dns: bool = True
        self.dns: list[str] = []

        # Linux only Used by PostUp script
        self.dns_search: list[str] = []
        self.dns_linux: bool = False
        self.dns_postup: str = ''
        self.dns_postdn: str = ''

        #
        # 3 states:
        #   active, inactive, hidden
        #   enum makes toml read/write complex so keep 2 bools
        #
        self.active: bool = True
        self.hidden: bool = False

        #
        # internal
        #
        self.is_gw: bool = False
        self.changed: bool = False
        self.mod_time = mod_time_now()

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)
