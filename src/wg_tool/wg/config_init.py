# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
 Create server config template
    - This will be marked changed by caller and written out as usual
"""
from crypto import gen_keys
from lib import current_date_time_str
from .class_serv import WgtServer

def _sample_server_config():
    """
    Make dictionary sample server config
    """
    mod_time = current_date_time_str(fmt='%y%m%d-%H:%M')
    (key_priv, key_pub, _key_psk) = gen_keys()
    serv_dict = {
            'active_users' : [],
            'Address' :  ['10.99.99.1/24', 'fc00:99:99::1/64'],
            'Hostname' :  'vpn.example.com',
            'Hostname_Int' :  'vpn.internal.example.com',
            'ListenPort' :  '39001',
            'ListenPort_Int' :  '39001',
            'PrivateKey' :  key_priv,
            'PublicKey' :  key_pub,
            'PostUp' :  '/usr/bin/nft -f /etc/wireguard/scripts/postup.nft',
            'PostDown' :  '/usr/bin/nft flush ruleset',
            'DNS_SEARCH' :  ['sales.example.com', 'example.com'],
            'DNS' :  ['10.99.99.21', '10.99.99.22'],
            'mod_time' : mod_time
            }
    return serv_dict

def initial_server_config(_wgtool):
    """
    Run once to get server template and one client template
        - do not overwrite exiting configs
    """
    print('Making sample server config - please edit for your setup')
    serv_dict = _sample_server_config()
    server = WgtServer(serv_dict)
    server.set_changed(True)
    return server
