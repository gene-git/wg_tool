# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
make private, public and preshared keys using wg genkey/pubkey/genpsk
"""
from utils.msg import (Msg)
from utils.run_prog_copy import (run_prog)


def gen_key_pair() -> tuple[str, str]:
    """
    Use /usr/bin/wg from wireguard tools to generate the public private
    and preshared keys.

    While we could generate directly, using the tools from wireguard ensures
    that we are consistent with what wireguard uses.

    Note, that time to generate keys is irrelevant.
    """
    key_prv: str = ''
    key_pub: str = ''

    #
    # private key
    #
    pargs = ['/usr/bin/wg', 'genkey']
    (ret, key_prv, errors) = run_prog(pargs)
    if ret != 0:
        Msg.err(f'Error generating key: {errors}')
        return ('', '')

    #
    # pub key
    #
    key_pub = public_from_private_key(key_prv)

    key_prv = key_prv.strip()
    key_pub = key_pub.strip()

    return (key_prv, key_pub)


def gen_psk() -> str:
    """
    Generate a WG pre shared key (PSK)
    """
    wg = '/usr/bin/wg'
    pargs = [wg, 'genpsk']

    (ret, psk, errors) = run_prog(pargs)
    if ret != 0:
        Msg.err(f'Error generating psk: {errors}')
        return ''
    psk = psk.strip()
    return psk


def public_from_private_key(key_prv: str) -> str:
    """
    Extract public key from private key
    """
    wg = '/usr/bin/wg'
    pargs = [wg, 'pubkey']

    (ret, key_pub, errors) = run_prog(pargs, input_str=key_prv)
    if ret != 0:
        Msg.err(f'Error generating psk: {errors}')
        return ''

    key_pub = key_pub.strip()

    return key_pub
