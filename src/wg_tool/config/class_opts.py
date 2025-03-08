# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
WgOpts  - command line options for WgTool
"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-statements
import argparse
from .options import available_options
from .options_save import read_merge_saved_opts, write_saved_opts

class WgtOpts:
    """
    Command line options
     - some may be optionally saved to file in config dir
    """
    def __init__(self, work_path, save_dir):
        gh_url:str = 'https://github.com/gene-git/wg_tool'
        desc: str = 'wg-tool : Manage wireguard Server & User/Profile configs'
        desc += f'\n{" ":10s}Detailed docs available at {gh_url}'

        self.work_dir = None
        self.init = False
        self.add_users = False
        self.mod_users = False

        self.save_dir: str = save_dir
        self.save_file : str= 'saved_options'

        #
        # User ips
        #
        self.default_prefixlen_4 = 32
        self.default_prefixlen_6 = 128
        self.prefixlen_4 = self.default_prefixlen_4
        self.prefixlen_6 = self.default_prefixlen_6

        self.ips_refresh = False
        self.allowed_ips = None
        self.upd_endpoint = False
        self.dns_search = False
        self.dns_linux = False
        self.int_serv = False
        self.upd_user_keys = False
        self.upd_serv_keys = False
        self.all_users = False
        self.active = False
        self.import_user = None
        self.list_users = False
        self.show_rpt = False
        self.run_show_rpt = False
        self.details = False
        self.save_opts = False

        self.file_perms = False
        self.verb = False
        self.version = False

        self.user_keepalive = 0

        #
        # These can be overriden from cli or from saved options
        #
        self.default_keep_hist = 5
        self.default_keep_hist_wg = 3

        self.keep_hist = self.default_keep_hist
        self.keep_hist_wg = self.default_keep_hist_wg

        opts = available_options(work_path)

        # provide opts to argparse
        par = argparse.ArgumentParser(description=desc,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
        for opt in opts:
            (opt_s, opt_l), kwargs = opt
            if opt_l :
                par.add_argument(opt_s, opt_l, **kwargs)
            else:
                par.add_argument(opt_s, **kwargs)

        parsed = par.parse_args()
        if parsed:
            # map each option to it's attribute
            for (opt, val) in vars(parsed).items() :
                setattr(self, opt, val)

        #
        # python 3.12 deprecated some argparse options such as 'type' : int
        #
        if self.prefixlen_4:
            self.prefixlen_4 = int(self.prefixlen_4)

        if self.prefixlen_6:
            self.prefixlen_6 = int(self.prefixlen_6)

        if self.keep_hist:
            self.keep_hist = int(self.keep_hist)

        if self.keep_hist_wg:
            self.keep_hist_wg = int(self.keep_hist_wg)

        if self.user_keepalive:
            self.user_keepalive = int(self.user_keepalive)

        #
        # for saved options, priority is:  command line, saved file, default
        #
        read_merge_saved_opts(self)

        if self.save_opts:
            write_saved_opts(self)

    def __getattr__(self, name):
        """ non-set items simply return None makes it easy to check existence"""
        return None

    def check(self):
        """
        consistency checks
          - one we had is no longer needed - keep method in case of future need?
        """
        okay = True
        return okay
