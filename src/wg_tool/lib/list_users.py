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

    msg('Summary of Users and Profiles:')
    if not users_profiles:
        msg('  No users found')
        return

    for (user_name, prof_names) in users_profiles.items():
        user = wgtool.users[user_name]
        user_act = wgtool.is_user_active(user_name)

        act_mark = '-'
        if user_act:
            act_mark = '+'

        user_str = f'{user_name:>15s} ({act_mark}) :'
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

    for (user_name, prof_names) in users_profiles.items():
        user = wgtool.users[user_name]
        act_mark = _marker_active(wgtool.is_user_active(user_name))

        user_str = f'{user_name:>15s} ({act_mark}) :'
        msg(user_str)

        for prof_name in prof_names :
            act_mark = _marker_active(user.is_profile_active(prof_name))
            this_prof = f'{prof_name} ({act_mark})'
            prof = user.profile[prof_name]

            msg(f'{this_prof:>25s}')
            msg(f'{"Address":>35s} : {prof.Address}')
            msg(f'{"PublicKey":>35s} : {prof.PublicKey}')
            msg(f'{"Endpoint":>35s} : {prof.Endpoint}')

        msg('')

def list_users(wgtool):
    """
    make a simple informational list of users/profiles
    """
    details = wgtool.opts.details

    users_profiles = cli_user_prof_names(wgtool)
    if not users_profiles or wgtool.opts.all_users:
        users_profiles = all_users_prof_names(wgtool)

    _user_summary(wgtool, users_profiles)
    if details:
        _user_details(wgtool, users_profiles)
