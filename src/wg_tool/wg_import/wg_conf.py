# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Data for a wireguard peer config
"""
# pylint: disable = too-few-public-methods
from utils import Msg
from utils import open_file
from vpn import Vpn

from .wg_conf_base import WgConfBase
from .wg_parse import wg_conf_parse
from .wg_conf_to_id import wg_conf_file_to_id
from .import_one import import_one
from .gw_infos import GwInfos


class WgConf(WgConfBase):
    """
    One Wireguard peer config
        - each "peer" is a gateway (Endpoint)
          which will become a separate profile.
    """
    def _read_config(self, file: str) -> bool:
        """
        Read wireguard config file
        """
        fob = open_file(file, 'r')
        if not fob:
            Msg.err(f'Error reading wireguard config {file}\n')
            return False

        conf_rows = fob.readlines()
        fob.close()

        if not wg_conf_parse(conf_rows, self):
            return False
        return True

    def load_wg_conf_file(self, file: str) -> bool:
        """
        Read the file, parse.
        """
        self.file = file
        id_str = wg_conf_file_to_id(file)
        if not id_str:
            Msg.err(f'Unable to extract ID from filename: {file}\n')
            return False

        self.ident.from_str(id_str)
        self.ident.new_tag()
        self.ident.refresh()
        if not self._read_config(file):
            return False
        return True

    def import_one(self, vpn: Vpn, gw_infos: GwInfos) -> bool:
        """
        Import data into vpn
        """
        return import_one(vpn, self, gw_infos)
