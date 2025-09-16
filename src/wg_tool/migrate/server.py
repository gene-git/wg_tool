# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
wg-tool server class
"""
# pylint: disable=too-few-public-methods
import os

from .server_data import ServerData


class Server(ServerData):
    """
    Server data
    """
    # pylint: disable=
    def __init__(self, work_dir: str):
        #
        # Data
        #  - track when data changes
        #
        super().__init__()
        self.okay: bool = True
        self.changed: bool = False

        #
        # Data File
        #
        db_dir = os.path.join(work_dir, 'configs', 'server')
        self.db_path = os.path.join(db_dir, 'server.conf')
        if not self.load(self.db_path):
            self.okay = False
