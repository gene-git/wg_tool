# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
WgOpts  - command line options for WgTool
"""
# pylint disable=R0902
import argparse
from .save_options import read_merge_saved_opts, write_saved_opts

class WgtOpts:
    """
    Manage command line options
    """
    # pylint: disable=R0903
    def __init__(self, work_path, save_dir):
        desc = 'WgTool : Manage wireguard Server & User/Profiles '
        #self.work_dir = work_dir
        self.save_dir = save_dir
        self.save_file = 'saved_options'

        #
        # These can be overriden from cli or from saved options
        #
        self.default_keep_hist = 5
        self.default_keep_hist_wg = 3

        opts = [
                [('-wkd', '--work_dir'),
                 {'help'        : f'Set the working dir. If unset, use dir path : {work_path} '}
                ],
                [('-i',   '--init'),
                 {'action'      : 'store_true',
                  'help'        : 'Initialize: create server config - please edit.' \
                                 +' Can also set --work_dir'}
                ],
                [('-add', '--add_users'),
                 {'action'      : 'store_true',
                  'help'        : 'Add user(s) and/or user profiles user:prof1,prof2,... '}
                ],
                [('-mod', '--mod_users'),
                 {'action'      : 'store_true',
                  'help'        : 'Modify user(s) profiles (with -dnsrch, -dnslin)'}
                ],
                [('-dnsrch', '--dns_search'),
                 {'action'      : 'store_true',
                  'help'        : 'Add/Mod user with dns search list from server config DNS_SEARCH'}
                ],
                [('-dnslin', '--dns_linux'),
                 {'action'      : 'store_true',
                  'help'        : 'Linux. profile resolv.conf managed using PostUp/Down scripts'}
                ],
                [('-int', '--int_serv'),
                 {'action'      : 'store_true',
                  'help'        : 'With --add_users uses internal wireguard server'}
                ],
                [('-uuk', '--upd_user_keys'),
                 {'action'      : 'store_true',
                  'help'        : 'Update existing user(s) keys.'}
                ],
                [('-usk', '--upd_serv_keys'),
                 {'action'      : 'store_true',
                  'help'        : 'Update server keys - affects all users'}
                ],
                [('-all', '--all_users'),
                 {'action'      : 'store_true',
                  'help'        : 'Some opts (e.g. upd_user_keys) may apply to all users/profiles'}
                ],
                [('-act', '--active'),
                 {'action'      : 'store_true',
                  'help'        : 'Mark users/profiles user[:profile,...] active'}
                ],
                [('-inact', '--inactive'),
                 {'action'      : 'store_true',
                  'help'        : 'Mark users/profiles user[:profile,...] inactive'}
                ],
                [('-imp', '--import_user'),
                 {'help'        : 'Import a user profile : --imp user.conf user_name:profile_name'}
                ],
                [('-keep', '--keep_hist'),
                 {'type'        : int,
                  #'default'     : self.keep_hist,
                  'help'        : 'Keep config history'}
                ],
                [('-keep_wg', '--keep_hist_wg'),
                 {'type'        : int,
                  #'default'     : self.keep_hist_wg,
                  'help'        : 'Keep wg-config history'}
                ],
                [('-l',   '--list_users'),
                 {'action'      : 'store_true',
                  'help'        : 'List users/profiles'}
                ],
                [('-rpt',   '--show_rpt'),
                 {'help'        : 'Output of "wg show" (file, "stdin") -> connected users report'}
                ],
                [('-rrpt',  '--run_show_rpt'),
                 {'action'      : 'store_true',
                  'help'        : 'Run "wg show" -> connected users report (see also -rpt)'}
                ],
                [('-det',   '--details'),
                 {'action'      : 'store_true',
                  'help'        : 'Adds details to rpt and list output'}
                ],
                [('-sop',   '--save_opts'),
                 {'action'      : 'store_true',
                  'help'        : 'Save defaults for keep_hist/keep_hist_wg '}
                ],
                [('-v',   '--verb'),
                 {'action'      : 'store_true',
                  'help'        : 'Be more verbose'}
                ],
                [('users', None),
                 {'nargs'       : '*',
                  'help'        : 'user_1[:prof1,prof2,...] user_2[:prof_1,prof_2]'}
                ],
               ]

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
