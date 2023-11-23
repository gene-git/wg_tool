# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Takes output from 'wg show' and adds user:profile
to any current connections.
"""
import sys
from .file_tools import open_file
from .run_prog import run_prog
from .cli_users import all_users_prof_names

def _user_by_pubkey_address(wgtool):
    """
    make look up tables for all known users
     - user by pub key
     - user by address
    """
    user_by_key = {}
    user_by_add = {}
    for user_name in wgtool.users_all:
        user = wgtool.users[user_name]
        user_act = wgtool.is_user_active(user_name)

        for prof_name in user.profile_names():
            prof = user.profile[prof_name]
            pub_key = prof.PublicKey
            address = prof.Address
            prof_act = user.is_profile_active(prof_name)

            user_by_key[pub_key] = {
                    'user_name' : user_name,
                    'prof_name' : prof_name,
                    'user_active' : user_act,
                    'prof_active' : prof_act,
                    }

            user_by_add[address] = {
                    'user_name' : user_name,
                    'prof_name' : prof_name,
                    'user_active' : user_act,
                    'prof_active' : prof_act,
                    }

    return (user_by_add, user_by_key)

def _parse_serv_users(_wgtool, report_in):
    """
    Parse the wg show output into serv and list of users
    A user is 'seen' if 'endpoint' is present - otherwise not.
     - 1 x serv_dict
     - List of user_dict
       1 item per 'peer'
    returns (serv_dict, user_dicts_list)

    wg_show output :
      interface: wg0
         public key: XXXXXXX
         private key: (hidden)
         listening port: <port>

       peer: <pub_key>
         preshared key: (hidden)
         endpoint: <source:ip>
         allowed ips: [user:profile Address]
         latest handshake: 11 seconds ago
         transfer: 21.57 KiB received, 120.62 KiB sent

       peer: <pub_key>
         allowed ips: 10.42.42.11/32

       peer: <pub_key>
         preshared key: (hidden)
         allowed ips: 10.42.42.22/32

    """
    rpt_lines = report_in.splitlines()

    serv_rpt = {
            'interface' : None,
            'pub_key' : None,
            'port' : None,
            }

    user_rpt_template = {
            'pub_key' : None,
            'address' : None,
            'endpoint' : None,      # <= means wg seen connection from here
            'handshake' : None,
            'transfer' : None,

            'user_name' : None,
            'prof_name' : None,
            'user_active' : None,
            'prof_active' : None,
            }

    user_rpts = []
    for row in rpt_lines:
        row = row.strip()
        if not row:
            continue

        key_val = row.split(':',1)
        if not key_val:
            continue

        key = None
        val = None
        key = key_val[0].strip()
        if len(key_val) > 1:
            val = key_val[1].strip()

        if key ==  'interface':
            serv_rpt["interface"] = val

        elif key ==  'peer':
            user_rpt = user_rpt_template.copy()
            user_rpts.append(user_rpt)
            user_rpt["pub_key"] = val

        elif key ==  'public key':
            serv_rpt["pub_key"] = val

        elif key ==  'listening port':
            serv_rpt["port"] = val

        elif key ==  'endpoint':
            user_rpt["endpoint"] = val

        elif key ==  'allowed ips':
            user_rpt["address"] = val

        elif key ==  'latest handshake':
            user_rpt["handshake"] = val

        elif key ==  'transfer':
            user_rpt["transfer"] = val

    return (serv_rpt, user_rpts)

def _analyze_report(wgtool, report_in):
    """
    Take wg show report - parse it into server and users
    Identify user:profile and return new report
      - users 'seen' by vpn have 'endpoint'
    """
    # pylint: disable=R0914,R0915

    (serv_rpt, user_rpts) = _parse_serv_users(wgtool, report_in)

    #
    # Match address / pub_key against known current users.
    # These are present for every user.
    # For users wg server has 'seen' there is also 'endpoint'
    #
    # Possible server has not been updated, and pub_key
    # may not match. address likely to remain same. But even there
    # it could change (delete re-create, manual edit etc.)
    # Make sure we handle such edge cases and warn appropriately
    #

    (user_by_add, user_by_key) = _user_by_pubkey_address(wgtool)

    all_okay = True
    for user_rpt in user_rpts:
        pub_key = user_rpt['pub_key']
        address = user_rpt['address']
        comment = ''

        info_key = user_by_key.get(pub_key)
        info_add = user_by_add.get(address)

        user_name = None
        prof_name = None
        user_act = False
        prof_act = False
        comment = None

        if info_key:
            user_name = info_key['user_name']
            prof_name = info_key['prof_name']
            user_act = info_key['user_active']
            prof_act = info_key['prof_active']
            if not info_add:
                all_okay = False
                comment = 'Mismatched address'

        elif info_add:
            all_okay = False
            comment = 'Mismatched Public key'
            user_name = info_add['user_name']
            prof_name = info_add['prof_name']
            user_act = info_add['user_active']
            prof_act = info_add['prof_active']

        else:
            all_okay = False
            comment = 'Unknown address and unknown public key'
            user_name = 'unknown'
            prof_name = 'unkown'

        user_rpt['user_name'] = user_name
        user_rpt['prof_name'] = prof_name
        user_rpt['user_active'] = user_act
        user_rpt['prof_active'] = prof_act
        user_rpt['comment'] = comment
        user_rpt['pub_key'] = pub_key
        user_rpt['address'] = address

    return (all_okay, serv_rpt, user_rpts)

def _rpt_user(wgtool, user):
    """
    Print report for one user
      user = user_dict created by _analyze_report()
    """
    # pylint: disable=R0914
    msg = wgtool.msg

    pub_key = user['pub_key']
    address = user['address']
    endpoint = user['endpoint']
    handshake = user['handshake']
    transfer = user['transfer']
    user_name = user['user_name']
    prof_name = user['prof_name']
    user_active = user['user_active']
    prof_active = user['prof_active']

    comment = user['comment']

    actu = '-'
    if user_active :
        actu = '+'
    actp = '-'
    if prof_active :
        actp = '+'

    if user_name:
        msg(f'{user_name:>12s} ({actu}) : {prof_name} ({actp})')
        if endpoint:
            msg(f'  {"endpoint":>14s} : {endpoint}')
        msg(f'  {"address":>14s} : {address}')
        msg(f'  {"pub_key":>14s} : {pub_key}')
        if handshake:
            msg(f'  {"handshake":>14s} : {handshake}')
        if transfer:
            msg(f'  {"transfer":>14s} : {transfer}')
    else:
        msg('user:prof not found')
        msg(f'  {"address":>14s} : {address}')
        msg(f'  {"pub_key":>14s} : {pub_key}')

    if comment:
        msg(f'  {"warn":>14s} : {comment}')

    msg('')


def _serv_user_profile_names(users_on_serv):
    """
    Make a list of users and profiles from server report
      Return dictionary of user_names,
    """
    user_profs = {}
    for user in users_on_serv:
        user_name = user.get("user_name")
        if user_name:
            prof_name = user.get('prof_name')
            if prof_name:
                if user_profs.get(user_name):
                    user_profs[user_name].append(prof_name)
                else:
                    user_profs[user_name] = [prof_name]
    return user_profs

def _any_missing_users(wgtool, users_on_serv):
    """
    Checks that every user/profile is actually in the running server config
    """
    msg = wgtool.msg
    wmsg = wgtool.wmsg

    users_profiles = all_users_prof_names(wgtool)
    if not users_profiles:
        return

    user_profs_serv = _serv_user_profile_names(users_on_serv)

    #
    # simple count check
    #
    warning_done = False
    num_users = len(users_profiles)
    num_on_serv = len(user_profs_serv)
    if num_users != num_on_serv:
        wmsg(' Missing current users\n')
        warning_done = True
        msg(f'  Expect {num_users}, got {num_on_serv}')

    #
    # check names
    #
    for (user_name, prof_names) in users_profiles.items():
        if not wgtool.is_user_active(user_name):
            continue

        if user_name not in user_profs_serv:
            if not warning_done:
                wmsg(' Missing current users\n')
            msg(f'  {"Missing":>15s} : {user_name}')
            continue

        user = wgtool.users[user_name]
        for prof_name in prof_names :
            if not user.is_profile_active(prof_name):
                continue

            if prof_name not in user_profs_serv[user_name]:
                if not warning_done:
                    wmsg(' Missing current users\n')
                msg(f'  {"Missing":>15s} : {user_name}:{prof_name}')

def _show_rpt_from_output(wgtool, output):
    """
    Takes output from 'wg show' as string
     - make report
    """
    # pylint: disable=R0914
    msg = wgtool.msg
    wmsg = wgtool.wmsg

    details = wgtool.opts.details

    (all_okay, serv, users) = _analyze_report(wgtool, output)

    #
    # Server
    #
    msg('wg server:')
    iface = serv['interface']
    pub_key = serv['pub_key']
    port = serv['port']

    msg(f'  {"interface":>14s} : {iface}')
    msg(f'  {"port":>14s} : {port}')
    msg(f'  {"pub_key":>14s} : {pub_key}')

    #
    # check server pub key is current
    #
    if pub_key != wgtool.server.PublicKey:
        wmsg(f'  {"Warn":>14s} : server pub key out of date')
        wmsg(f'  {"Expected":>14s} : {wgtool.server.PublicKey}')
    #
    # users - seen / connected
    #
    msg('\nwg users seen/connected:')
    for user in users:
        if user["endpoint"]:
            _rpt_user(wgtool, user)

    if details:
        msg('\nwg other users :')
        for user in users:
            if not user["endpoint"]:
                _rpt_user(wgtool, user)

    if not all_okay:
        wmsg('  Warning: not all user:prof found or perfectly matched.')
        wmsg('  Check server has current wg0.conf and/or restart')

    #
    # check for any missing users
    #
    _any_missing_users(wgtool, users)

def show_rpt(wgtool, file_in):
    """
    Read output of "wg show" from file or on stdin.
    Identify connected user profiles
    """
    # pylint: disable=R0914
    emsg = wgtool.emsg

    if file_in == 'stdin':
        wg_show_output = sys.stdin.read()
    else :
        fobj = open_file(file_in, 'r')
        if fobj:
            wg_show_output = fobj.read()
            fobj.close()
        else:
            emsg('Error in show_rpt:  failed to read file : {file_in}')
            return

    _show_rpt_from_output(wgtool, wg_show_output)

def run_show_rpt(wgtool):
    """
    runs wg show and then generate report
    """
    msg = wgtool.msg
    emsg = wgtool.emsg

    pargs = ['/usr/bin/wg', 'show']
    [retc, output, errors] = run_prog(pargs)

    if retc != 0:
        emsg('Failed running "wg show"')
        msg(errors)
    else:
        _show_rpt_from_output(wgtool, output)
