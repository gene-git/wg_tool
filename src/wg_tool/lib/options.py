# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Options - command line options for WgTool
"""
# pylint: disable=too-many-statements

def available_options(work_path:str):
    """
    Manage command line options
    """
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

    ohelp = 'Modify user(s) profiles (with -dnsrch, -dnslin, -upd, -ips)'
    opt = [('-mod', '--mod_users'), {'help' : ohelp, act : act_on}]
    opts.append(opt)

    ohelp = 'cidr prefix length for profile ipv4 addresses (32)'
    opt = [('-pfxlen_4', '--prefixlen_4'), {'help' : ohelp}]
    opts.append(opt)

    ohelp = 'cidr prefix length for profile ipv6 addresses (128)'
    opt = [('-pfxlen_6', '--prefixlen_6'), {'help' : ohelp}]
    opts.append(opt)

    ohelp = 'Refresh profile IPs if needed'
    opt = [('-ips', '--ips_refresh'), {'help' : ohelp, act : act_on}]
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
    opt = [('-imp', '--import_user'), {'help' : ohelp}]
    opts.append(opt)

    ohelp = 'Keep config history'
    opt = [('-keep', '--keep_hist'), {'help' : ohelp}]
    opts.append(opt)

    ohelp = 'Keep wg-config history'
    opt = [('-keep_wg', '--keep_hist_wg'), {'help' : ohelp}]
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

    ohelp = 'Save defaults for keep_hist[_wg] and prefixlen_[4/6] '
    opt = [('-sop',   '--save_opts'), {'help' : ohelp, act : act_on}]
    opts.append(opt)

    ohelp = 'Be more verbose'
    opt = [('-v', '--verb'), {'help' : ohelp, act : act_on}]
    opts.append(opt)

    ohelp = 'Version info'
    opt = [('-V', '--version'), {'help' : ohelp, act : act_on}]
    opts.append(opt)

    ohelp = 'user_1[:prof1,prof2,...] user_2[:prof_1,prof_2] ...'
    opt = [('users', None), {'help' : ohelp, 'nargs' : '*'}]
    opts.append(opt)

    return opts
