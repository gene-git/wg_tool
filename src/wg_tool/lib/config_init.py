"""
 Create server config template
    - This will be marked changed by caller and written out as usual
"""
from .keys import gen_keys

def _sample_server_config():
    """
    Make dictionary sample server config
    """
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
            'DNS' :  ['10.99.99.21', '10.99.99.22'],
            }
    return serv_dict

def initial_server_config(_wgtool):
    """
    Run once to get server template and one client template
        - do not overwrite exiting configs
    """
    print('Making sample server config - please edit for your setup')
    serv_dict = _sample_server_config()
    return serv_dict
