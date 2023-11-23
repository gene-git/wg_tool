# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
 Import existing user from standard wireguard user.conf file
 This is same file output write_wg_users()

 Check that file is consistent with our server config
   User fields
    PrivateKey
    PresharedKey
    Address     - check this IP is consistent and available

   Server fields - change if different and warn as users existing config may not work
    DNS            - may or may not work
    AllowedIPs          maybe
    Endpoint            wont work if changed
    PublicKey           wont work if changed

    Access :  --import file.conf                -> user_name : file, config : main
              --import file.conf user_1:laptop  -> user_name : user_1, config : laptop
"""
import os
from .utils import open_file
from .users import cli_user_prof_names
from .find_user_ip import is_user_address_available
from .keys import public_from_private_key

def _clean_line(line):
    line = line.strip()
    if line.startswith("#"):
        return None
    line = line.split("#")[0]
    if line:
        line = line.strip()
    return line

def _read_wg_user_config(wgtool, fname):
    """
    Read in wg user .conf file
    """
    # pylint: disable=R0914
    wmsg = wgtool.wmsg

    if not os.path.exists(fname):
        wmsg(f'No such user conf file to import: {fname}')
        return (None, None)

    fobj = open_file(fname, 'r')
    if fobj:
        data = fobj.readlines()
        fobj.close()
    else:
        wmsg(f'Failed to read user config to import {fname}')
        return None

    DNS = []
    PresharedKey = None
    for row in data:
        row = _clean_line(row)
        if not row :
            continue

        val = None
        if '=' in row:
            [key, val] = row.split('=',1)
            key = key.strip()
            val = val.strip()
        else:
            key = row

        _section = None
        match(key):
            case '[Interface]':
                _section = 'Interface'
            case '[Peer]':
                _section = 'Peer'

            # only in Interface - could check but not necessary
            case 'PrivateKey':
                PrivateKey = val
            case 'Address':
                Address = val
            case 'DNS':
                DNS.append(val)

            # only in Peer - could check but not necessary
            case 'PublicKey':
                PublicKey = val
            case 'PresharedKey':
                PresharedKey = val
            case 'AllowedIPs':
                AllowedIPs = val
            case 'Endpoint':
                Endpoint = val
                [Hostname, ListenPort] = Endpoint.split(':')

    conf_user = {
            'Address'       : Address,
            'PrivateKey'    : PrivateKey,
            'PresharedKey'  : PresharedKey,
            }
    conf_serv = {
            'PublicKey'     : PublicKey,
            'AllowedIPs'    : AllowedIPs,
            'Endpoint'      : Endpoint,
            'Hostname'      : Hostname,
            'ListenPort'    : ListenPort,
            'DNS'           : DNS,
            }

    return (conf_user, conf_serv)


def import_user(wgtool):
    """
    Import wg user.conf
    Access :
        --import file.conf                -> user_name : file, config : main
        --import file.conf user_1:laptop  -> user_name : user_1, config : laptop
    """
    # pylint: disable=R0914
    wmsg = wgtool.wmsg
    emsg = wgtool.emsg

    okay = True
    conf_file = wgtool.opts.import_user

    #
    # use user_name:prof_name if specified
    # otherwise use filename without '.conf'
    #
    users_profiles = cli_user_prof_names(wgtool)
    if users_profiles:
        num_users_cli = len(users_profiles)
        if num_users_cli > 1:
            wmsg(f'Import user requires exactly one user[:profile] not {num_users_cli}')
            return not okay

        # already checked length is exactly 1
        (user_name, prof_names) = list(users_profiles.items())[0]
        if prof_names :
            prof_name = prof_names[0]
            if len(prof_names) > 1:
                emsg(f'Import {conf_file} for user {user_name} must have max of 1 proile name')
                return not okay
    else:
        user_name = conf_file.replace('.conf','')
        prof_name = 'main'

    #
    # Read the file
    #  - parse it into server part (conf_serv)
    #                    user part (conf_user)
    #
    (conf_user, conf_serv) = _read_wg_user_config(wgtool, conf_file)
    if not (conf_user and conf_serv):
        return not okay

    #
    # Check server and user parts
    #
    (serv_okay, int_ext) = _check_server_fields(wgtool, conf_serv)
    user_okay = _check_user_fields(wgtool, conf_user)

    if serv_okay and user_okay :
        user = _make_new_user(wgtool, user_name, prof_name, int_ext, conf_user)
        if not user:
            emsg(f'Failed to add new user: {user_name} {prof_name} from file {conf_file}')
            return not okay
        return okay

    emsg('Import failed')
    return not okay

def _check_user_fields(wgtool, conf_user):
    """
    check for non empty keys and non-duplicate ip
    """
    wmsg = wgtool.wmsg
    okay = True

    if not conf_user['PrivateKey']:
        okay = False
        wmsg('Import: missing PrivateKey')

    Address = conf_user['Address']
    if Address:
        ip_avail = is_user_address_available(wgtool, Address)
        if not ip_avail:
            okay = False
            wmsg('Import: Address already taken {Address}')
    else:
        okay = False
        wmsg('Import: missing Address')

    return okay

def _check_server_fields(wgtool, conf_serv):
    """
    Check that things are consistent with our server config
    """
    wmsg = wgtool.wmsg
    msg = wgtool.msg

    okay = True
    int_ext = None
    server = wgtool.server

    # public key
    got = conf_serv['PublicKey']
    if got != server.PublicKey:
        okay = False
        wmsg('Import: mismatched server public key')
        msg(f'     got: {got}')
        msg(f'  expect: {server.PublicKey}')

    # hostname
    got = conf_serv['Hostname']
    if got == server.Hostname:
        int_ext = 'external'
    elif server.Hostname_Int and got == server.Hostname_Int:
        int_ext = 'internal'
    else:
        okay = False
        wmsg('Import: mismatched Hostname')
        msg(f'     got: {got}')
        msg(f'  expect: {server.Hostname}')
        if server.Hostname_Int:
            msg('    or')
            msg(f'  expect: {server.Hostname_Int}')

    # allowed IPs
    got = conf_serv['AllowedIPs']
    serv_val = server.user_allowedips()
    if got != serv_val:
        okay = False
        wmsg('Import: mismatched AllowedIPs')
        msg(f'     got: {got}')
        msg(f'  expect: {serv_val}')

    # listen port
    got = conf_serv['ListenPort']
    if int_ext == 'external':
        serv_val = server.ListenPort
    else:
        serv_val = server.ListenPort_Int

    if got != serv_val:
        okay = False
        wmsg(f'Import: mismatched listen port {int_ext}')
        msg(f'     got: {got}')
        msg(f'  expect: {serv_val}')


    # DNS - must be at least a subset of current list
    got = conf_serv['DNS']
    for item in got:
        if item not in server.DNS:
            okay = False
            wmsg(f'Import: DNS address not same as current server {item}')

    return (okay, int_ext)

def _make_new_user(wgtool, user_name, prof_name, int_ext, conf_user):
    """
    Generate user_dict to install as new user
    """
    server = wgtool.server
    if int_ext == 'external':
        Endpoint = server.endpoint()
    else:
        Endpoint = server.endpoint_int()
    AllowedIPs = server.user_allowedips()

    Address = conf_user['Address']
    PrivateKey = conf_user['PrivateKey']
    PresharedKey = conf_user.get('PresharedKey')

    PublicKey = public_from_private_key(PrivateKey)
    prof_dict = {
            'Address'       : Address,
            'PrivateKey'    : PrivateKey,
            'PublicKey'     : PublicKey,
            'AllowedIPs'    : AllowedIPs,
            'Endpoint'      : Endpoint,
            }

    if PresharedKey:
        prof_dict['PresharedKey'] = PresharedKey

    user_dict = {prof_name : prof_dict}
    user = wgtool.add_user(user_name, prof_name, user_dict)
    return user
