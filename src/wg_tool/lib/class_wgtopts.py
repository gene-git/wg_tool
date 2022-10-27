"""
WgOpts  - command line options for WgTool
"""
# pylint disable=R0902
import argparse
from .save_options import read_cli_opts, write_cli_opts

class WgtOpts:
    """
    Manage command line options
    """
    # pylint: disable=R0903
    def __init__(self, save_dir):
        desc = 'WgTool : Manage wireguard Server & User/Profiles '
        self.save_dir = save_dir
        self.save_file = 'saved_options'
        self.keep_hist = 5
        self.keep_hist_wg = 3

        read_cli_opts(self)

        opts = [
                [('-i',   '--init'),
                 {'action'      : 'store_true',
                  'help'        : 'Initialize - make server config template - please edit'}
                ],
                [('-add', '--add_users'),
                 {'action'      : 'store_true',
                  'help'        : 'Add user(s) and/or user profiles user:prof1,prof2,... '}
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
                  'default'     : self.keep_hist,
                  'help'        : f'Keep config history (default {self.keep_hist})'}
                ],
                [('-keep_wg', '--keep_hist_wg'),
                 {'type'        : int,
                  'default'     : self.keep_hist_wg,
                  'help'        : f'Keep wg-config history (default {self.keep_hist_wg})'}
                ],
                [('-l',   '--list_users'),
                 {'action'      : 'store_true',
                  'help'        : 'List users/profiles'}
                ],
                [('-sop',   '--save_opts'),
                 {'action'      : 'store_true',
                  'help'        : 'Save defaults for keep_hist/keep_hist_wg '}
                ],
                [('-rpt',   '--show_rpt'),
                 {'help'        : 'Output of "wg show" (file, "stdin") -> connected users report'}
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
            # set each option to be an attribute
            for (opt, val) in vars(parsed).items() :
                setattr(self, opt, val)

        if self.save_opts:
            write_cli_opts(self)

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
