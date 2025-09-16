# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Phase 2:
    Update gateway and psks
"""
# pylint: disable=too-many-branches
from py_cidr import Cidr

from utils import Msg
from vpn import Vpn
from net import internet_networks

from .gw_info import GwInfo
from .wg_conf_base import WgDns


def find_gateway_profs(vpn: Vpn, info:  dict[str, GwInfo]) -> bool:
    """
    Find profile from the pubkey
    """
    for (pubkey, gwinfo) in info.items():
        prof = vpn.prof_from_pubkey(pubkey)
        if prof:
            gwinfo.prof = prof
        else:
            Msg.err(f'Error: no gateway profile found for pubkey: {pubkey}\n')
            return False
    return True


def update_dns(vpn, wg_dns: WgDns) -> bool:
    """
    [Interface] section exposes DNS used by each peer.

    Find common dns hosts and move them to vpninfo
    NB the tool leaves any gateway DNS alone, so
    remove from client profiles
    """
    dns_common: list[str] = []
    for (host, count) in wg_dns.dns.items():
        if count >= wg_dns.num_cl:
            dns_common.append(host)

    if not dns_common:
        return True

    #
    # Add to vpninfo, remove from client profile
    # per WG a dns item can be IP which is a dns server
    # or non-IP in which case its a search domain
    # We must leave them as they come (e.g. if see
    # a 'search' domain - it can have an IP so we must
    # not do reverse dns on it. Follow the wg rule exactly.
    #
    servers: list[str] = []
    search: list[str] = []
    for host in dns_common:
        if Cidr.is_valid_cidr(host):
            servers.append(host)
        else:
            search.append(host)

    vpninfo = vpn.vpninfo
    if servers:
        if vpninfo.dns:
            vpninfo.dns = list(set(vpninfo.dns + servers))
        else:
            vpninfo.dns = servers

    if search:
        if vpninfo.dns_search:
            vpninfo.dns_search = list(set(vpninfo.dns_search + search))
        else:
            vpninfo.dns_search = search

    return True


def update_gateways(vpn, infos: list[GwInfo]) -> bool:
    """
    Use info gathered from every [Peer] section to
    update gateways:
        - nets offered
        - endpoint (now shown as 'xxx.xxx:port')
          port here is from Interface ListenPort - must math
          what peers use to connect to gateway - peers know full endpoint.
          mismatched ports is warning only, as port forwarding could be used.
    """
    internets = internet_networks()

    for info in infos:
        #
        # Endpoint
        #
        prof = info.prof
        if info.endpoint:
            if not prof.Endpoint or ':' not in prof.Endpoint:
                prof.Endpoint = info.endpoint

        #
        # nets offered
        #
        if info.nets_offered:
            cidrs = list(set(info.nets_offered))
            nets: list[str] = []
            for cidr in cidrs:
                if cidr in internets:
                    prof.internet_offered = True
                else:
                    nets.append(cidr)

            if prof.nets_offered:
                prof.nets_offered += nets
            else:
                prof.nets_offered = nets
            prof.nets_offered = list(set(prof.nets_offered))

    #
    # Check for peer to peer
    # If we see any peer with short prefix then
    # some are peer to peer - we support all or none.
    # Its simpler and must be > 1 to be useful anyway.
    peer_to_peer = False
    for info in infos:
        for cidr in info.vpn_nets:
            iptype = Cidr.cidr_iptype(cidr)
            net = Cidr.cidr_to_net(cidr)
            if not net:
                continue

            if iptype == 'ip4' and net.prefixlen < 32:
                peer_to_peer = True
                break

            if iptype == 'ip6' and net.prefixlen < 128:
                peer_to_peer = True
                break

    if peer_to_peer:
        vpn.vpninfo.peer_to_peer = True

    #
    # DNS
    #   Drop any dns in profile if same host is in vpninfo
    #
    dns_updated: list[str] = []
    vpn_dns = vpn.vpninfo.dns
    for info in infos:
        prof = info.prof
        dns_updated = []
        for dns in prof.dns:
            if dns not in vpn_dns:
                dns_updated.append(dns)
        prof.dns = dns_updated

    return True


def update_psks(vpn, infos: list[GwInfo]) -> bool:
    """
    Use info gathered from every [Peer] section to
    update psks.

    Configs use public ip from which we now get profile.
    From there we get tag and update psk.
    Each gateway info.psks is {peer-tag: psk}
    """
    psks = vpn.vpninfo.psks

    for info in infos:
        gw_tag = info.prof.ident.tag
        for (tag, psk) in info.psks.items():
            if psk:
                psks.put_shared_key(gw_tag, tag, psk)
    return True
