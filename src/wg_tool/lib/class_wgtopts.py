# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
WgOpts  - command line options for WgTool
"""
# pylint: disable=too-many-statements
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

        opts = []
        act = 'action'
        act_on = 'store_true'

        ohelp = f'Set the working dir. If unset, use dir path : {work_path}'
        opt = [('-wkd', '--work_dir'), {'help' : ohelp}]
        opts.append(opt)

        ohelp = 'Initialize: create server config - please edit.  May use --work_dir'
        opt = [('-i', '--init'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Add user(s) and/or user profiles user:prof1,prof2,... '
        opt = [('-add', '--add_users'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Modify user(s) profiles (with -dnsrch, -dnslin, -upd)'
        opt = [('-mod', '--mod_users'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Ensure user(s) profiles use current endpoint (add -int if needed)'
        opt = [('-upd', '--upd_endpoint'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Add/Mod user with dns search list from server config DNS_SEARCH'
        opt = [('-dnsrch', '--dns_search'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Linux. profile resolv.conf managed using PostUp/Down scripts'
        opt = [('-dnslin', '--dns_linux'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'With --add_users uses internal wireguard server'
        opt = [('-int', '--int_serv'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Update existing user(s) keys.'
        opt = [('-uuk', '--upd_user_keys'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Update server keys - affects all users'
        opt = [('-usk', '--upd_serv_keys'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Apply to all users/profiles used with: -usk and -mod'
        opt = [('-all', '--all_users'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Mark users/profiles user[:profile,...] active'
        opt = [('-act', '--active'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Mark users/profiles user[:profile,...] inactive'
        opt = [('-inact', '--inactive'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Import a user profile : --imp user.conf user_name:profile_name'
        opt = [('-imp', '--import_user'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Keep config history'
        opt = [('-keep', '--keep_hist'), {'help' : ohelp, 'type' : int}]
        opts.append(opt)

        ohelp = 'Keep wg-config history'
        opt = [('-keep_wg', '--keep_hist_wg'), {'help' : ohelp, 'type' : int}]
        opts.append(opt)

        ohelp = 'List users/profiles'
        opt = [('-l', '--list_users'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Output of "wg show" (file, "stdin") -> connected users report'
        opt = [('-rpt',   '--show_rpt'), {'help' : ohelp}]
        opts.append(opt)

        ohelp = 'Run "wg show" -> connected users report (see also -rpt)'
        opt = [('-rrpt',  '--run_show_rpt'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Adds more detail to rpt and list output'
        opt = [('-det',   '--details'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Save defaults for keep_hist/keep_hist_wg '
        opt = [('-sop',   '--save_opts'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'Be more verbose'
        opt = [('-v', '--verb'), {'help' : ohelp, act : act_on}]
        opts.append(opt)

        ohelp = 'user_1[:prof1,prof2,...] user_2[:prof_1,prof_2] ...'
        opt = [('users', None), {'help' : ohelp, 'nargs' : '*'}]
        opts.append(opt)

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
