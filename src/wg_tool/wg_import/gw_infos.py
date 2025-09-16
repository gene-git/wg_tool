# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Data for a wireguard peer config
"""
# pylint disable = invalid-name
# pylint: disable = too-few-public-methods
# pylint disable = too-many-instance-attributes
from utils.debug import pprint
from vpn import Vpn

from .gw_info import GwInfo
from .wg_conf_base import WgDns
from .update import find_gateway_profs
from .update import update_dns
from .update import update_gateways
from .update import update_psks


class GwInfos:
    """
    Used to gather gateway info from [Peer] sections
    info = {pubkey: GwInfo}
    """
    def __init__(self):
        # gather info for each gateway
        self.info: dict[str, GwInfo] = {}

        # gather DNS from each peer
        self.wg_dns: WgDns = WgDns()

    def update_gateways(self, vpn: Vpn) -> bool:
        """
        Use the info collected from all the config peers
        to update gateway and psks
        """
        #
        # find profile for each gateway pubkey
        #
        if not find_gateway_profs(vpn, self.info):
            return False

        infos_list: list[GwInfo] = list(self.info.values())

        if not update_dns(vpn, self.wg_dns):
            return False

        if not update_gateways(vpn, infos_list):
            return False

        if not update_psks(vpn, infos_list):
            return False

        return True

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)
