# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Data for a wireguard peer config
"""
# pylint: disable = invalid-name
# pylint: disable = too-few-public-methods
# pylint: disable = too-many-instance-attributes
from utils import clean_comment
from utils import csv_string_to_list
from crypto import public_from_private_key
from net import wq_addresses_to_addresses

from .wg_conf_base import WgConfBase
from .wg_conf_base import WgConfPeer


def wg_conf_parse(rows: list[str], conf: WgConfBase) -> bool:
    """
    Parse one wireguard config

    Interface comes first followed by 1 or more Peers.
    """
    if not rows:
        return True

    interface = conf.interface
    for row in rows:
        row = clean_comment(row)
        if not row:
            continue
        #
        # key or key = value
        #
        val = ''
        if '=' in row:
            [key, val] = row.split('=', 1)
            key = key.strip()
            val = val.strip()
        else:
            key = row

        match key:
            case '[Peer]':
                peer = WgConfPeer()
                conf.peers.append(peer)

            case 'PublicKey':
                peer.PublicKey = val

            case 'PresharedKey':
                peer.PresharedKey = val

            case 'Endpoint':
                peer.Endpoint = val

            case 'AllowedIPs':
                val_list = csv_string_to_list(val)
                if peer.AllowedIPs:
                    peer.AllowedIPs += val_list
                else:
                    peer.AllowedIPs = val_list

            case 'PrivateKey':
                interface.PrivateKey = val
                interface.pubkey = public_from_private_key(val)

            case 'Address':
                val_list = csv_string_to_list(val)
                addrs = wq_addresses_to_addresses(val_list)
                if interface.Address:
                    interface.Address += addrs
                else:
                    interface.Address = addrs

            case 'DNS':
                val_list = csv_string_to_list(val)
                if interface.DNS:
                    interface.DNS += val_list
                else:
                    interface.DNS = val_list

            case 'PersistentKeepalive':
                peer.PersistentKeepalive = int(val)

            case 'ListenPort':
                interface.ListenPort = val

            case 'PreUp':
                interface.PreUp = [val]

            case 'PreDown':
                interface.PreDown = [val]

            case 'PostUp':
                interface.PostUp = [val]

            case 'PostDown':
                interface.PostDown = [val]

            case 'MTU':
                interface.MTU = val

    return True
