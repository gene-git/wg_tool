"""
 Generate wireguard user config and QR code for all users
   - don't limit to active users that only affects server config
"""
# pylint: disable=C0103,R0914,R1732

from .utils import open_file
from .file_tools import setup_save_path
from .file_tools import file_symlink
from .file_tools import save_prev_symlink
from .file_tools import format_file_header
from .file_check_match import file_check_match

def _serv_conf_str(wgtool):
    """
    generate server part of wg0.conf as string
    """
    serv = wgtool.server

    Address = ', '.join(serv.Address)
    ListenPort = serv.ListenPort
    PrivateKey = serv.PrivateKey
    #PublicKey = serv.PublicKey
    PostUp = serv.PostUp
    PostDown = serv.PostDown


    conf = ''
    conf += '[Interface]\n'
    conf += f'{"Address":15s} = {Address}\n'
    conf += f'{"ListenPort":15s} = {ListenPort}\n'
    conf += f'{"PrivateKey":15s} = {PrivateKey}\n'
    #conf += f'{"PublicKey":15s} = {PublicKey}\n'
    conf += '\n'
    conf += f'{"PostUp":15s} = {PostUp}\n'
    conf += f'{"PostDown":15s} = {PostDown}\n'
    conf += '\n'
    conf += '#' + 60*'-' + '\n\n'

    return conf

def _one_user_conf_str(user_name, conf_name, config):
    """
    Each peer is few items from user config
    """
    PublicKey = config.PublicKey
    PresharedKey = config.PresharedKey
    AllowedIPs = config.Address              ## N.B this is -not- AllowedIPs

    conf = '\n'
    conf += f'{"[Peer]":15s} # {user_name} {conf_name}\n'
    conf += f'{"PublicKey":15s} = {PublicKey}\n'
    if PresharedKey:
        conf += f'{"PresharedKey":15s} = {PresharedKey}\n'
    conf += f'{"AllowedIPs":15s} = {AllowedIPs}\n'

    return conf

def _users_conf_str(wgtool):
    """
    generate users part of wg0.conf as string
      - only add active_users and configs
    """
    vmsg = wgtool.vmsg
    server = wgtool.server
    active_users = server.active_users

    users_conf_str = ''
    if not active_users:
        return users_conf_str
    for user_name in active_users:
        if user_name in wgtool.users:
            user = wgtool.users[user_name]
            active_profiles = user.active_profiles

            if not active_profiles:
                vmsg(f'User {user} has no active profiles')
                continue

            for prof_name in active_profiles:
                profile = user.profile[prof_name]
                this_conf_str = _one_user_conf_str(user_name, prof_name, profile)
                users_conf_str += this_conf_str
        else:
            vmsg(f'Active user {user_name} has no profile - ignoring')

    return users_conf_str

def write_wg_server(wgtool):
    """
    generate wg server config wg0.con :
    """
    errors = 0
    msg = wgtool.msg
    vmsg = wgtool.vmsg
    emsg = wgtool.emsg

    #wgtool.refresh_active_users()

    serv_dir = wgtool.wg_serv_dir
    conf_file = wgtool.wg_serv_conf_file

    comment = f' Wireguard server {conf_file}'
    header = format_file_header(comment, wgtool.now)
    serv_str = _serv_conf_str(wgtool)
    users_str = _users_conf_str(wgtool)

    full_conf_str = serv_str + users_str

    (actual_file, link_name, link_targ) = setup_save_path(wgtool, serv_dir, conf_file, mkdirs=False)

    #
    # if same - dont write
    #
    is_same = file_check_match(link_name, header, full_conf_str)
    if is_same:
        vmsg(f'{"wg-config":>10s}: up to date - {conf_file}')
    else:
        (actual_file, link_name, link_targ) = setup_save_path(wgtool, serv_dir, conf_file, mkdirs=True)
        msg(f'{"wg-config":>10s}:   updating - {conf_file}')
        fobj = open_file(actual_file, 'w')
        if fobj:
            fobj.write(header)
            fobj.write(full_conf_str)
            fobj.close()
            save_prev_symlink(serv_dir, link_name)
            file_symlink(link_targ, link_name)
        else:
            errors += 1
            emsg('Failed to write server config {actual_file}')

    return errors
