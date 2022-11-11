"""
   key changes for server or user profiles
"""
from .keys import gen_keys
from .cli_users import cli_user_prof_names
from .cli_users import all_users_prof_names
from .utils import current_date_time_str

def upd_user_keys(wgtool):
    """
    For (specified or all) users update their keys
      - key rollover for user level
    """
    msg = wgtool.msg
    vmsg = wgtool.vmsg
    emsg = wgtool.emsg
    okay = True

    users_profiles = cli_user_prof_names(wgtool)
    if wgtool.opts.all_users:
        if not users_profiles:
            users_profiles = all_users_prof_names(wgtool)
        else:
            emsg('Add user keys: specify users or "--all_users" not both')
            return not okay

    for (user_name, prof_names) in users_profiles.items():
        msg(f'Updating keys for {user_name}')
        user = wgtool.users[user_name]

        for prof_name in prof_names :
            profile = user.profile[prof_name]
            vmsg(f'    {prof_name}')
            (key_priv, key_pub, key_psk) = gen_keys()

            profile.PrivateKey = key_priv
            profile.PublicKey = key_pub
            profile.PresharedKey = key_psk

            profile.mod_time = current_date_time_str(fmt='%y%m%d-%H:%M')

            wgtool.user_changed(user_name)

    return okay

def upd_serv_keys(wgtool):
    """
    Update server keys
      - user profiles will need to be updated with server's new public key
    """
    msg = wgtool.msg
    okay = True
    server = wgtool.server
    msg('Updating server keys')

    (key_priv, key_pub, _key_psk) = gen_keys()
    server.PrivateKey = key_priv
    server.PublicKey = key_pub

    server.mod_time = current_date_time_str(fmt='%y%m%d-%H:%M')
    wgtool.server.set_changed(True)

    if okay:
        okay = upd_user_serv_key(wgtool)

    return okay

def upd_user_serv_key(wgtool):
    """
    Update all user profiles with server public key
    """
    msg = wgtool.msg
    vmsg = wgtool.vmsg

    okay = True
    users_profiles = all_users_prof_names(wgtool)

    for (user_name, prof_names) in users_profiles.items():
        msg(f'Updating server public key for {user_name}:')
        user = wgtool.users[user_name]
        user.date = wgtool.now
        for prof_name in prof_names :
            vmsg(f'    {prof_name}')
            profile = user.profile[prof_name]
            profile.PublicKey = wgtool.server.PublicKey
            profile.mod_time = current_date_time_str(fmt='%y%m%d-%H:%M')
        wgtool.user_changed(user_name)
    return okay
