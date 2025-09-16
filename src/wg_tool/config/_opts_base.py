# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
OptsBase
 - configuration and command line options.
"""
# pylint: disable=too-many-instance-attributes, too-few-public-methods
import os

from data import mod_time_now
from utils.debug import pprint
from ids import Identities

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
        self.data_dir: str = 'Data'

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
