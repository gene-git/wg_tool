"""
Takes output from 'wg show' and adds user:profile
to any current connections.
"""
import sys
from .file_tools import open_file

def _user_by_pubkey(wgtool):
    """
    make look up table by pub key of all users.
    """
    user_by_key = {}
    for user_name in wgtool.users_all:
        user = wgtool.users[user_name]
        user_act = wgtool.is_user_active(user_name)

        for prof_name in user.profile_names():
            prof = user.profile[prof_name]
            pub_key = prof.PublicKey
            prof_act = user.is_profile_active(prof_name)

            user_by_key[pub_key] = {
                    'user_name' : user_name,
                    'prof_name' : prof_name,
                    'user_active' : user_act,
                    'prof_active' : prof_act,
                    }

    return user_by_key

def _parse_wg_show(wgtool, report_in):
    """
    Take wg show report - filter out connected users
    Identify user:profile and return new report

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
            'endpoint' : None,
            'handshake' : None,
            'transfer' : None,

            'user_name' : None,
            'prof_name' : None,
            'user_active' : None,
            'prof_active' : None,
            }

    user_rpts = []

    #
    # parse the data
    #
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

        match(key):
            case  'interface':
                serv_rpt["interface"] = val

            case  'peer':
                user_rpt = user_rpt_template.copy()
                user_rpt["pub_key"] = val

            case  'public key':
                serv_rpt["pub_key"] = val

            case  'listening port':
                serv_rpt["port"] = val

            case  'endpoint':
                user_rpt["endpoint"] = val
                user_rpts.append(user_rpt)

            case  'allowed ips':
                user_rpt["address"] = val

            case  'latest handshake':
                user_rpt["handshake"] = val

            case  'transfer':
                user_rpt["transfer"] = val

    #
    # make it more useful
    # Lets check connections belong to active users - if not likely wg server needs restarting
    # with updated config
    #
    user_by_key = _user_by_pubkey(wgtool)
    for user_rpt in user_rpts:
        pub_key = user_rpt['pub_key']
        info = user_by_key[pub_key]

        user_rpt['user_name'] = info['user_name']
        user_rpt['prof_name'] = info['prof_name']
        user_rpt['user_active'] = info['user_active']
        user_rpt['prof_active'] = info['prof_active']

    return (serv_rpt, user_rpts)

def show_rpt(wgtool, file_in):
    """
    Read output of "wg show" on our stdin.
    Identify connected user profiles
    """
    # pylint: disable=R0914
    msg = wgtool.msg
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

    (serv, users) = _parse_wg_show(wgtool, wg_show_output)

    msg('wg server:')
    iface = serv['interface']
    pub_key = serv['pub_key']
    port = serv['port']
    msg(f'  {"interface":>14s} : {iface}')
    msg(f'  {"port":>14s} : {port}')
    msg(f'  {"pub_key":>14s} : {pub_key}')

    msg('\nwg users:')
    for user in users:
        pub_key = user['pub_key']
        address = user['address']
        endpoint = user['endpoint']
        handshake = user['handshake']
        transfer = user['transfer']
        user_name = user['user_name']
        prof_name = user['prof_name']
        user_active = user['user_active']
        prof_active = user['prof_active']

        actu = '- '
        if user_active :
            actu = '+'
        actp = '-'
        if prof_active :
            actp = '+'

        msg(f'{user_name:>12s} ({actu}) : {prof_name} ({actp})')
        msg(f'  {"endpoint":>14s} : {endpoint}')
        msg(f'  {"address":>14s} : {address}')
        msg(f'  {"handshake":>14s} : {handshake}')
        msg(f'  {"transfer":>14s} : {transfer}')
        msg('')
