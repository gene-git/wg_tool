# SPDX-License-Identifier: MIT
# Copyright (c) 2022,2023 Gene C
"""
   create new users / profiles
"""
from .cli_users import cli_user_prof_names
from .cli_users import all_users_prof_names

def _user_summary(wgtool, users_profiles):
    """
    Summary of all known users /profiles names
     - (+) or (-) for active or inactive
    """
    msg = wgtool.msg

    msg('Users & Profiles Summary:')
    if not users_profiles:
        msg('  No users found')
        return
    #
    # Sort by user name
    #
    users_profs_sorted = dict(sorted(users_profiles.items()))

    for (user_name, prof_names) in users_profs_sorted.items():
        user = wgtool.users[user_name]
        user_act = wgtool.is_user_active(user_name)

        act_mark = '-'
        if user_act:
            act_mark = '+'

        dts = ''
        if user.mod_time:
            # just the date - time only with detail
            dts = user.mod_time
            dts = dts[0:6]

        user_str = f'{user_name:>15s} ({act_mark}) {dts} :'
        msg(user_str, end='')

        prof_str = ''
        for prof_name in prof_names :
            prof_act = user.is_profile_active(prof_name)
            act_mark = '-'
            if prof_act:
                act_mark = '+'
            this_prof = f'{prof_name} ({act_mark})'
            prof_str += f'{this_prof:>12s} '

        msg(f'{"":1s} {prof_str}')

def _marker_active(act):
    """ return act/inactive marker """
    marker = '-'
    if act:
        marker = '+'
    return marker

def _user_details(wgtool, users_profiles):
    """
    Summary of all known users /profiles names
     - (+) or (-) for active or inactive
    """
    msg = wgtool.msg

    msg('\nDetails of Users and Profiles:')
    if not users_profiles:
        msg('  No users found')
        return
    users_profs_sorted = dict(sorted(users_profiles.items()))

    line = 40*'-'
    for (user_name, prof_names) in users_profs_sorted.items():
        user = wgtool.users[user_name]
        act_mark = _marker_active(wgtool.is_user_active(user_name))

        mod_time = ''
        if user.mod_time:
            mod_time = user.mod_time
        msg(f'{line:>43s}')
        user_str = f'{user_name:>15s} ({act_mark}) {mod_time:15s}'
        msg(user_str)
        msg(f'{line:>43s}')

        first = True
        for prof_name in prof_names :
            act_mark = _marker_active(user.is_profile_active(prof_name))
            this_prof = f'{prof_name} ({act_mark})'
            prof = user.profile[prof_name]

            mod_time = ''
            if prof.mod_time:
                mod_time = prof.mod_time
                #msg(f'{"Mod_Date":>41s} : {prof.mod_time}')

            if first:
                first = False
            else:
                msg('')
            msg(f'{this_prof:>32s} {mod_time:>23s}')
            msg(f'{"Address":>41s} : {prof.Address}')
            msg(f'{"PublicKey":>41s} : {prof.PublicKey}')
            msg(f'{"Endpoint":>41s} : {prof.Endpoint}')

        #msg('')

def list_users(wgtool):
    """
    make a simple informational list of users/profiles
    """
    details = wgtool.opts.details

    users_profiles = cli_user_prof_names(wgtool)

    # if user given but without profiles - list all profiles
    users_profs = {}
    for (user_name,prof_names) in users_profiles.items():
        if prof_names:
            users_profs[user_name] = prof_names
        else:
            user = wgtool.users[user_name]
            users_profs[user_name] = user.profile_names()

    users_profiles = users_profs


    if not users_profiles or wgtool.opts.all_users:
        users_profiles = all_users_prof_names(wgtool)

    _user_summary(wgtool, users_profiles)
    if details:
        _user_details(wgtool, users_profiles)
