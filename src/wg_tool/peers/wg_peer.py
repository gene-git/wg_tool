# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Write wireguard all config files for one vpn
"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
from py_cidr import Cidr

from utils import Msg
from utils import list_string_to_csv_sublists
from net import internet_networks

from .profile_base import ProfileBase


class WgPeerData:
    """
    [Peer] part of wireguard config
    """
    def __init__(self):
        self.config_prof: ProfileBase
        self.prof: ProfileBase
        self.alternate: bool
        self.psk: str
        self.nets_common: list[str]
        self.peer_to_peer: bool
        self.vpn_nets: list[str]

    def data(self) -> str:
        """
        Return the [Peer] section data.
        Can be empty if alternate requested and no
        alternate Endpoint.
        """
        data = _wg_peer_data(self)
        return data


def _wg_peer_data(wg_peer: WgPeerData) -> str:
    """
    For profile 'my_prof', create data for peer profile 'prof'.
    Caller must ensure peer_prof != my_prof
    my_prof - owns the config.
    prof is the peer to be added
    psk is the shared key for the pair : (my_prof,  prof)
    cl_nets_offered: list of networks clients provide to all gatways
                    and clients of those gateways can access via the gateway.

    If alternate is set then alternate endpoint is used. Caller will
    only call us with alternate if prof is gateway and exists.
    We dont need to check this but can if we'er cautious.
    """
    my_prof = wg_peer.config_prof
    prof = wg_peer.prof

    if wg_peer.alternate:
        if not (my_prof.alternate_wanted and prof.Endpoint_alt):
            return ''

    alt_mark = 'alternate' if wg_peer.alternate else ''
    gw_mark = '(gateway)' if prof.is_gw else ''

    note = f'{prof.ident.acct_name} {prof.ident.prof_name}'

    data: str = '\n'
    data += f'{"[Peer]":20s} # {note} {gw_mark} {alt_mark}\n'
    data += f'{"PublicKey":20s} = {prof.PublicKey}\n'

    #
    # check if (my_prof) config is for gateway
    #
    if my_prof.is_gw:
        data += _peer_data_gateway(wg_peer)
    else:
        data += _peer_data_client(wg_peer)

    #
    # Endpoint:
    #   Gateway peers have endpoint
    #
    endpoint = _endpoint(note, prof, wg_peer.alternate)
    if endpoint:
        data += endpoint

    return data


def _peer_data_gateway(wg_peer: WgPeerData) -> str:
    """
    One peer section.
    my_prof - owns the config and is a gateway.
    prof is the peer to be added
    """
    data: str = ''
    internet = internet_networks()

    my_prof = wg_peer.config_prof
    prof = wg_peer.prof
    psk = wg_peer.psk
    peer_to_peer = wg_peer.peer_to_peer
    vpn_nets = wg_peer.vpn_nets

    #
    # PSK
    #   - if gateway pair use that psk
    #   - if (client) peer has psk use that
    #
    # psk: str = ''
    # if gw_psk:
    #     psk = gw_psk
    # elif prof.PresharedKey:
    #     psk = prof.PresharedKey
    if psk:
        data += f'{"PresharedKey":20s} = {psk}\n'

    #
    # Allowed ips
    #  - profile vpn Address + any additional internals permitted
    #
    allowed: list[str] = []
    if peer_to_peer:
        allowed = vpn_nets
    else:
        allowed = prof.Address.copy()

    if prof.internet_offered and not my_prof.internet_offered:
        allowed += internet

    if wg_peer.nets_common:
        allowed += wg_peer.nets_common

    # if prof.nets:
    #     allowed += prof.nets

    #
    # compact (keep pre-compact as comment)
    #
    if allowed:
        allowed = list(set(allowed))
        allowed = Cidr.sort_cidrs(allowed)
        compact = Cidr.compact(allowed)
        if len(compact) < len(allowed):
            data += _pre_compact_nets_comment(allowed)
        allowed = compact

    # Up to 3 nets per AllowedIPs line
    sub_allowed = list_string_to_csv_sublists(allowed, 3)
    for allowed_ips in sub_allowed:
        data += f'{"AllowedIPs":20s} = {allowed_ips}\n'

    return data


def _peer_data_client(wg_peer: WgPeerData) -> str:
    """
    One peer section.
    my_prof - owns the config and is a client (not a gateway)
    prof is the peer to be added
    """
    data: str = ''
    internet = internet_networks()

    my_prof = wg_peer.config_prof
    prof = wg_peer.prof
    psk = wg_peer.psk
    peer_to_peer = wg_peer.peer_to_peer
    vpn_nets = wg_peer.vpn_nets

    #
    # This client PSK is shared with gateway
    #
    if psk:
        data += f'{"PresharedKey":20s} = {psk}\n'

    if prof.PersistentKeepalive > 0:
        data += f'{"PersistentKeepalive":20s} = {prof.PersistentKeepalive}\n'

    #
    # Allowed ips
    #
    allowed: list[str] = []
    if peer_to_peer:
        allowed = vpn_nets
    else:
        allowed = prof.Address.copy()

    if my_prof.internet_wanted:
        allowed += internet

    if wg_peer.nets_common:
        allowed += wg_peer.nets_common
    #
    # compact if asked (keep pre-compact as comment)
    #
    if allowed:
        allowed = list(set(allowed))
        allowed = Cidr.sort_cidrs(allowed)
        compact = Cidr.compact(allowed)
        if len(compact) < len(allowed):
            data += _pre_compact_nets_comment(allowed)
        allowed = compact

    # Up to 3 nets per AllowedIPs line
    sub_allowed = list_string_to_csv_sublists(allowed, 3)
    for allowed_ips in sub_allowed:
        data += f'{"AllowedIPs":20s} = {allowed_ips}\n'

    return data


def _endpoint(note: str, prof: ProfileBase, alternate: bool) -> str:
    """
    Gateway peers must have endpoint
    """
    data: str = ''
    if prof.is_gw:
        if alternate:
            alt = 'alt-'
            endpoint = prof.Endpoint_alt
        else:
            alt = ''
            endpoint = prof.Endpoint
        if endpoint:
            data += f'{"Endpoint":20s} = {endpoint}\n'
        else:
            Msg.err(f'{note} : gateway peer missing an {alt}endpoint\n')
    return data


def _pre_compact_nets_comment(nets: list[str]) -> str:
    """
    Return comment string showing nets before they are compacted
    """
    comment: str = ''
    if not nets:
        return comment

    #
    # Use up to 3 nets per line
    #
    nets_sublists = list_string_to_csv_sublists(nets, 3)
    name = 'pre-compacted'
    for sub in nets_sublists:
        comment += f'# {name:20s} {sub}\n'

    return comment
