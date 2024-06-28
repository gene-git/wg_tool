# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
   create new users / profiles
"""
# pylint: disable=invalid-name
from .keys import gen_keys
from .cli_users import cli_user_prof_names
from .cli_users import all_users_prof_names

def _make_new_user(wgtool, user_name, prof_name, prof_dict):
    """
    add new user / profile
      - caller already checked user doesn't exist
    """
    user_dict = { prof_name : prof_dict }
    user = wgtool.add_user(user_name, prof_name, user_dict)
    return user

def _make_new_profile_dict(wgtool):
    """
    make a new user profile dict
      - for new or existing user (we dont need to know user name)
    """
    server = wgtool.server

    if wgtool.opts.int_serv:
        Endpoint = server.endpoint_int()
    else:
        Endpoint = server.endpoint()

    Address = wgtool.find_avail_user_ip()

    AllowedIPs = server.user_allowedips()
    allowed_ips_own = False
    if wgtool.opts.allowed_ips :
        if wgtool.opts.allowed_ips.lower() != 'default' and wgtool.opts.allowed_ips != AllowedIPs:
            AllowedIPs = wgtool.opts.allowed_ips
            allowed_ips_own = True

    DnsSearch = False
    if wgtool.opts.dns_search:
        DnsSearch = True

    DnsLinux = False
    if wgtool.opts.dns_linux:
        DnsLinux = True

    (key_priv, key_pub, key_psk) = gen_keys()

    prof_dict = {}
    prof_dict['Address'] = Address
    prof_dict['PrivateKey'] = key_priv
    prof_dict['PublicKey'] = key_pub
    prof_dict['PresharedKey'] = key_psk
    prof_dict['AllowedIPs'] = AllowedIPs
    prof_dict['Endpoint'] = Endpoint
    prof_dict['DnsSearch'] = DnsSearch
    prof_dict['DnsLinux'] = DnsLinux
    prof_dict['allowed_ips_own'] = allowed_ips_own

    return prof_dict

def _add_user_profiles(wgtool, user_name, prof_names):
    """
    Add user and/or profile(s)
    """
    okay = True

    if prof_names:
        prof_names_use = prof_names
    else:
        prof_names_use = ['main']

    for prof_name in prof_names_use:
        prof_dict = _make_new_profile_dict(wgtool)
        user_dict = { prof_name : prof_dict }
        wgtool.add_user(user_name, prof_name, user_dict)

    return okay

def add_users(wgtool):
    """
    Add new user and/or user profiles
      - Takes user/prof names from command line
      - existing user/profiles are left alone
        - checks for conflicts
    """
    wmsg = wgtool.wmsg

    okay = True
    users_profiles = cli_user_prof_names(wgtool)
    if not users_profiles:
        wmsg('Missing user(s) : None given on command line; ignoring')
        return okay

    for (user_name, prof_names) in users_profiles.items():
        _add_user_profiles(wgtool, user_name, prof_names)
        #wgtool.user_changed(user_name)
    return okay

def mod_users(wgtool):
    """
    Modify existing user:profile(s)
      - Takes user/prof names from command line
      - Must specify users - could extend to apply to all - safer this way.
      - mods:
        - dns_search (add dns search to dns)
        - dns_linux (use linux resolv.conf manager)
    """
    wmsg = wgtool.wmsg

    okay = True
    users_profiles = cli_user_prof_names(wgtool)
    if not users_profiles:
        if wgtool.opts.all_users:
            users_profiles = all_users_prof_names(wgtool)
        else:
            wmsg('Missing user:profile(s) : None given on command line; ignoring')
            return okay

    for (user_name, prof_names) in users_profiles.items():
        if not prof_names:
            wmsg(f'Modify user {user_name} requires profile name - skipped')
            continue
        for prof_name in prof_names:
            wgtool.mod_user_profile(user_name, prof_name)
        #wgtool.user_changed(user_name)
    return okay

def remove_active_users_profiles(wgtool):
    """
    For every user:profile
      - remove user from active_users
      - remove profile from that users active_profiles

      - if user and no profiles, mark user inactive
      - if user and profiles - mark only profiles inactive

    """
    msg = wgtool.msg
    wmsg = wgtool.wmsg

    okay = True
    users_profiles = cli_user_prof_names(wgtool)
    if not users_profiles:
        wmsg('Remove active user/profile(s) : None given on command line; ignoring')
        return okay

    for (user_name, prof_names) in users_profiles.items():
        # in case no profiles
        if not prof_names:
            msg('  Removing active user')
            msg(f'    {user_name}')
            wgtool.remove_active_user(user_name)
        else:
            msg(f'  Removing active profile for {user_name}')
            for prof_name in prof_names:
                msg(f'    {prof_name}')
                wgtool.remove_active_user_profile(user_name, prof_name)
                wgtool.user_changed(user_name)

    return okay

def add_active_users_profiles(wgtool):
    """
    Add new user and/or user profiles
      - Takes user/prof names from command line
      - existing user/profile are left alone
        - checks for conflicts
    """
    msg = wgtool.msg
    wmsg = wgtool.wmsg

    okay = True
    users_profiles = cli_user_prof_names(wgtool)
    if not users_profiles:
        wmsg('Missing active user/profile(s) : None on command line; ignoring')
        return okay

    for (user_name, prof_names) in users_profiles.items():
        # in case no profiles
        msg(f'Adding active user: {user_name}')
        wgtool.add_active_user(user_name)
        for prof_name in prof_names:
            msg(f'  {prof_name}')
            wgtool.add_active_user_profile(user_name, prof_name)

    return okay
