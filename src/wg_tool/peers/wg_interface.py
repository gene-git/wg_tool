# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Write wireguard all config files for one vpn
"""
from utils import Msg
from utils import list_string_to_csv_sublists
from vpninfo import VpnInfo

from .profile_base import ProfileBase
from .wg_dns import dns_to_wg_dns


def wg_interface_data(acct_info: str,
                      vpninfo: VpnInfo,
                      prof: ProfileBase) -> str:
    """
    Build WG interface section.

    Args:
        acct_info (str):
            Comment to be added after [Interface]

        vpninfo (VpnInfo):
            Use it's dns information.

    Returns:
        (str):
            data_string
    """
    data: str = ''
    data += f'{"[Interface]":20s} # {acct_info}\n'
    data += f'{"PrivateKey":20s} = {prof.PrivateKey}\n'

    #
    # Get the appropriate dns info
    #
    (dns_list, dns_search, dns_postup, dns_postdn) = _dns_data(vpninfo, prof)

    wg_dns = dns_list + dns_search

    if prof.is_gw:
        data += _interface_data_gateway(acct_info, prof)
    else:
        data += _interface_data_client(acct_info, wg_dns, prof)

    #
    # Pre up/down
    #
    pre_updn = _pre_updn(prof)
    if pre_updn:
        data += pre_updn

    #
    # Post up/down
    #
    post_updn = _post_updn(dns_postup, dns_postdn, prof)
    if post_updn:
        data += post_updn

    return data


def _interface_data_gateway(acct_info: str, prof: ProfileBase) -> str:
    """
    Build WG interface section for gateway profile.
    Returns:
        (str):
            data_string
    """
    data: str = ''

    port = _endpoint_to_listenport(prof.Endpoint)
    if not port:
        port = '51820'
    data += f'{"ListenPort":20s} = {port}\n'

    # We do 1 per line but can also be comma separated
    if prof.AddressWg:
        # gateway use AddressWg not Address like clients
        addresses = prof.AddressWg

        # Up to 3 addresses per line
        sub_addrs = list_string_to_csv_sublists(addresses, 3)
        for addr in sub_addrs:
            data += f'{"Address":20s} = {addr}\n'
    else:
        Msg.err(f'Gateway {acct_info} missing AddressWg\n')
        Msg.plain(f' Address = {prof.Address}\n')

    return data


def _interface_data_client(acct_info: str,
                           dns_list: list[str],
                           prof: ProfileBase) -> str:
    """
    Build the interface section

    Returns
        (success, data_string)
    """
    data: str = ''

    if prof.Address:
        # clients use Address not AddressWg like gateways
        addresses = prof.Address

        # Up to 3 addresses per line
        sub_addrs = list_string_to_csv_sublists(addresses, 3)
        for addr in sub_addrs:
            data += f'{"Address":20s} = {addr}\n'
    else:
        Msg.err(f'{acct_info} : missing Address\n')

    #
    # dns servers listed on if not dns_linux
    #
    if dns_list and not prof.dns_linux:
        for dns in dns_list:
            data += f'{"DNS":20s} = {dns}\n'

    return data


def _dns_data(vpninfo: VpnInfo, prof: ProfileBase
              ) -> tuple[list[str], list[str], str, str]:
    """
    Returns list of dns servers and
    for linux clients returns the postup/dn commands.
    These will be appended to any other postup/dn commands in
    the profile.

    Returns
        (dns_list, dns_search_list, dns_postup_cmd, dns_postdn_cmd)
    """
    #
    # dns servers only if dns_linux (and therefore postup/postdn not set).
    # dns servers:
    #   profile + [gateways + vpninfo] if usinf vpn dns

    dns_list: list[str] = prof.dns
    dns_search_list: list[str] = prof.dns_search
    dns_postup: str = ''
    dns_postdn: str = ''

    if prof.use_vpn_dns:
        # dns servers
        if vpninfo.dns_gateways:
            dns_list += vpninfo.dns_gateways

        if vpninfo.dns:
            dns_list += vpninfo.dns

        # dns search domains
        if vpninfo.dns_search_gateways:
            dns_search_list += vpninfo.dns_search_gateways

        if vpninfo.dns_search:
            dns_search_list += vpninfo.dns_search
    #
    # Keep the order the same dropping any duplicates
    #
    clean: list[str] = []
    for item in dns_list:
        if item not in clean:
            clean.append(item)
    dns_list = clean

    #
    # Wireguard requires IP for dns server and non-IP for search domain.
    # DNS query any non-IP hosynames to IP addresses.
    #
    dns_list = dns_to_wg_dns(dns_list, vpninfo.dns_lookup_ipv6)

    clean = []
    for item in dns_search_list:
        if item not in clean:
            clean.append(item)
    dns_search_list = clean

    #
    # Linux clients may use dns_postup/dn
    #
    if dns_list and prof.dns_linux:
        #
        # create postup/dn command strings
        #
        dns_postup = f'{vpninfo.dns_script} --up'
        dns_postdn = f'{vpninfo.dns_script} --down'

        dns_str = ','.join(dns_list)
        dns_postup += f' --dns_ips {dns_str}'

        if dns_search_list:
            dns_str = ','.join(dns_search_list)
            dns_postup += f' --dns_search {dns_str}'

    return (dns_list, dns_search_list, dns_postup, dns_postdn)


def _endpoint_to_listenport(endpoint: str) -> str:
    """
    Endpoint is: <ip>:<port>
    Return port. If no port empty string is returned.
    """
    if not endpoint:
        return ''

    (_addr, _delim, port) = endpoint.rpartition(':')
    return port


def _pre_updn(prof: ProfileBase) -> str:
    """
    Pre up/down
    """
    data: str = ''
    if prof.pre_up:
        pre_up = '; '.join(prof.pre_up)
        data += f'{"PreUp":20s} = {pre_up}\n'

    if prof.pre_down:
        pre_down = '; '.join(prof.pre_down)
        data += f'{"PreDown":20s} = {pre_down}\n'

    return data


def _post_updn(dns_postup: str, dns_postdn: str, prof: ProfileBase) -> str:
    """
    Post up/down
    Start with profile.post_up/dn
    Then append dns_postup/dn
    """
    data: str = ''
    post_up: str = ''

    #
    # post up
    #
    if prof.post_up:
        post_up = '; '.join(prof.post_up)

    if dns_postup:
        if post_up:
            post_up += '; '
        post_up += dns_postup

    if post_up:
        data += f'{"PostUp":20s} = {post_up}\n'

    #
    # post down
    #
    post_down: str = ''
    if prof.post_down:
        post_down = '; '.join(prof.post_down)

    if dns_postdn:
        if post_down:
            post_down += '; '
        post_down += dns_postdn

    if post_down:
        data += f'{"PostDown":20s} = {post_down}\n'

    return data
