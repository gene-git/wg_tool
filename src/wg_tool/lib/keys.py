"""
make private, public and preshared keys using wg genkey/pubkey/genpsk
"""
# pylint: disable=C0103
from .run_prog import run_prog

def gen_keys():
    """ use wg to generate public private and preshared keys """
    key_prv = None
    key_pub = None
    key_psk = None

    # private key
    wg = '/usr/bin/wg'
    pargs = [wg, 'genkey']
    [_ret, key_prv, _errors] = run_prog(pargs)

    # public key from private
    #if key_prv:
    #    pargs = [wg, 'pubkey']
    #    [_ret, key_pub, _errors] = run_prog(pargs, input_str=key_prv)
    key_pub = public_from_private_key(key_prv)

    # psk
    pargs = [wg, 'genpsk']
    [_ret, key_psk, _errors] = run_prog(pargs)

    key_prv = key_prv.strip()
    key_pub = key_pub.strip()
    key_psk = key_psk.strip()

    return key_prv, key_pub, key_psk

def public_from_private_key(key_prv):
    """
    Extract public key from private key
    """
    wg = '/usr/bin/wg'
    pargs = [wg, 'pubkey']
    [_ret, key_pub, _errors] = run_prog(pargs, input_str=key_prv)
    key_pub = key_pub.strip()

    return key_pub
