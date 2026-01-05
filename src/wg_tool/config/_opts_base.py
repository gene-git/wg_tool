# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
OptsBase
 - configuration and command line options.
"""
# pylint: disable=too-many-instance-attributes, too-few-public-methods
import os

from wg_tool.data import mod_time_now
from wg_tool.data import get_data_dir
from wg_tool.utils.debug import pprint
from wg_tool.ids import Identities

from .work_dir import (find_work_dir)


class OptsBase:
    """
    Config and Command line options
     - some may be optionally saved to file.
    """
    def __init__(self):
        #
        # Fix date/time so all use same
        #
        self.okay: bool = True
        self.now = mod_time_now()
        self.cwd = os.getcwd()

        # self.init: bool = False
        # self.add_users: bool = False
        # self.mod_users: bool = False

        self.paths: str = '/etc/wireguard/wg-tool:./'
        self.data_dir: str = get_data_dir()

        # Default - may be changed on command line
        self.work_dir: str = find_work_dir(self.paths, self.data_dir)

        #
        # Handled by mods/xxx
        #
        self.edit: bool = False
        self.copy: bool = False
        self.rename: bool = False
        self.new: bool = False
        self.modify: bool = False
        self.nets_wanted_add: list[str] = []
        self.nets_wanted_del: list[str] = []
        self.nets_offered_add: list[str] = []
        self.nets_offered_del: list[str] = []

        self.merge: str = ''

        self.ident: str = ''
        self.to_ident: str = ''

        #
        # Handled by vpns
        #
        self.active: bool = False
        self.not_active: bool = False
        self.hidden: bool = False
        self.not_hidden: bool = False

        self.roll_keys: bool = False
        self.refresh: bool = False
        self.import_configs: str = ''

        #
        # autosave options
        #
        self.hist: int = 5
        self.hist_wg: int = 3
        # self.net_compact: bool = True

        self.list: bool = False
        self.show_rpt: str = ''
        self.run_show_rpt: bool = False

        self.file_perms: bool = False

        self.brief: bool = False
        self.verb: int = 0
        self.version: bool = False

        self.migrate: bool = True

        #
        # IP Groups
        # A new peer with group membership <group-name>
        #   --new --ip-groups <comma-sep list of names> <vpn>.<account>.<profile>
        # ident can only use ip_group to add one group membership at a time.
        # We could make this a list ?
        #
        # New vpn with ip-group
        #   --new --add-ip-group <group-name> subnet1,subnet2 --ident <vpn>
        #
        #
        self.add_ip_group_name: str = ''
        self.add_ip_group_subnets: list[str] = []
        self.ip_group: str = ''

        self.allow_ip_groups: list[str] = []

        #
        # Command line address - can for 1 vpn on command line.
        # peer_names:
        # list of ID string "names" given on command line.
        # name format is:
        #   "<vpn>.<account>.<profile>
        # This list of IDs is installed in peer_ids class.
        #
        # pid_names -> peer id_names
        # pids -> peer identities
        #
        self.ident_names: list[str] = []
        self.idents: Identities = Identities()

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)
