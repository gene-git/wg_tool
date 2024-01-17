# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
WgOpts  - command line options for WgTool
"""
# pylint: disable=too-many-statements
import argparse
from .options import available_options
from .save_options import read_merge_saved_opts, write_saved_opts

class WgtOpts:
    """
    Manage command line options
    """
    # pylint: disable=R0903
    def __init__(self, work_path, save_dir):
        desc = 'wg-tool : Manage wireguard Server & User/Profile configs'
        #self.work_dir = work_dir
        self.save_dir = save_dir
        self.save_file = 'saved_options'

        #
        # User ips
        #
        self.default_prefixlen_4 = 32
        self.default_prefixlen_6 = 128

        #
        # These can be overriden from cli or from saved options
        #
        self.default_keep_hist = 5
        self.default_keep_hist_wg = 3

        opts = available_options(work_path)

        # provide opts to argparse
        par = argparse.ArgumentParser(description=desc)
        for opt in opts:
            (opt_s, opt_l), kwargs = opt
            if opt_l :
                par.add_argument(opt_s, opt_l, **kwargs)
            else:
                par.add_argument(opt_s, **kwargs)

        parsed = par.parse_args()
        if parsed:
            #
            # make each option an attribute
            #
            for (opt, val) in vars(parsed).items() :
                setattr(self, opt, val)

        #
        # for saved, prio is:  command line, saved file, default
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
