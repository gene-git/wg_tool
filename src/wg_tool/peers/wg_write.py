# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Write wireguard all config files for one vpn
"""
# pylint: disable=too-many-locals
import os

from data import mod_time_now
from data import get_wg_vpn_dir
from data import write_db_file
from data import restrict_file_mode

from utils import Msg
from utils import text_to_qr_file
from utils import make_dir_path
from utils import os_unlink

from .profile_base import ProfileBase

from .wg_interface import wg_interface_data
from .wg_peer import WgPeerData
from .wg_config_base import WgConfigBase


def wg_write_config(wg_conf: WgConfigBase,
                    acct_name: str,
                    prof_name: str) -> bool:
    """
    Write wireguard config for acct.profile

    If any gateway peer have alternate endpoint,
    then a second config written to the "alt" subdirectory.
    This has same [Interface] but gateway peers use the
    alternate endpoint.
    """
    alternate = False
    ok = _wg_write_config(wg_conf, acct_name, prof_name, alternate)
    if not ok:
        return False

    #
    # Could there be gateway which has alternate peer gateway?
    # or is alternate only applicable to client configs
    #
    acct = wg_conf.accts[acct_name]
    prof = acct.profile[prof_name]
    if prof.alternate_wanted and wg_conf.gw_alternates:
        alternate = True
        ok = _wg_write_config(wg_conf, acct_name, prof_name, alternate)
        if not ok:
            return False
    return True


def _wg_write_config(wg_conf: WgConfigBase,
                     acct_name: str,
                     prof_name: str,
                     alternate: bool
                     ) -> bool:
    """
    Write wireguard profile for one acct.

    Gateways:
        Each gateway profile has its [Interface] section
        and a [Peer] section for every other peer (client or gateway)
        where the gateways have an Endpoint

        If a gateway has an alternate endpoint, then it is written
        in the alt subdirectory.

        Clients have no endpoint.

    Clients:
        Each client profile has its [Interface] section
        and a [Peer] section for each gateway.
        A gateway peer includes it's Endpoint.

    Gateway config is similar to client config but
    includes a [Peer] section for every client not just gateways
    """
    all_okay: bool = True
    acct = wg_conf.accts[acct_name]
    prof = acct.profile[prof_name]
    vpninfo = wg_conf.vpninfo
    vpn_name = vpninfo.name
    work_dir = wg_conf.opts.work_dir

    #
    # when vpninfo.peer_to_peer is on, use network prefix
    # instead of single IP for AllowedIPs
    # (NB requires gateway to have ip forwarding on)
    #
    vpn_nets = vpninfo.get_cidrs()

    gw_mark = '(gateway)' if prof.is_gw else ''
    alt_mark = 'alternate' if alternate else ''
    acct_info = f'{acct_name} {prof_name} {gw_mark} {alt_mark}'

    Msg.plainverb(f'{"":4s} {acct_info}\n', level=3)

    #
    # Top of config file
    #
    data = _file_header(prof)

    acct_dir = _get_acct_dir(work_dir, vpn_name, acct_name)
    if not acct_dir:
        return False

    #
    # [Interface]
    #   Address here is wireguard IP (host bits with vpn prefix)
    #
    interface_data = wg_interface_data(acct_info, vpninfo, prof)
    data += interface_data
    data += '\n'

    #
    # [Peer]
    #   - Gateways
    #
    gateway_data = _wg_write_peer_gateways(wg_conf, vpn_nets, prof, alternate)
    if alternate and not gateway_data:
        return True
    data += gateway_data

    #
    # [Peer]
    #   - Clients (only in gateway configs)
    #
    if prof.is_gw:
        data += _wg_write_peer_clients(wg_conf, vpn_nets, prof)

    #
    # Write the config
    #
    config_name = prof_name
    alt = ''
    if alternate:
        acct_dir = os.path.join(acct_dir, 'Alt')
        config_name = prof_name + '-alt'
        alt = '(alternate) '

    fpath = os.path.join(acct_dir, f'{config_name}.conf')

    #
    # When checking if data/file are different, some comments are ones we
    # we want to not ignore.
    #
    ok_comments = ['pre-compact', 'vpn-name', 'account-name', 'profile-name',
                   'is-gateway']
    (ok, changed) = write_db_file(data, fpath, ok_comments=ok_comments)
    if not ok:
        Msg.err(f'Error writing wg config: {fpath}\n')
        all_okay = False

    if changed:
        id_str = prof.ident.id_str
        Msg.plain(f'      {id_str} wg config {alt}updated\n')

    #
    # Generate QR code (not for gateways)
    # - dont keep history for these as trivial
    #   generate - they're just QR of corresponding .conf file.
    # Only generate qr if the wg config changed
    # delete qr code if gateway and exists
    #
    qr_dir = _get_qr_dir(acct_dir)
    qr_file = os.path.join(qr_dir, f'{config_name}.png')
    if prof.is_gw:
        if os.path.isfile(qr_file):
            os_unlink(qr_file)
    elif changed:
        fmode = restrict_file_mode()
        if not text_to_qr_file(data, qr_file, fmode):
            # annoying not fatal
            Msg.warn(f'Error creating QR code: {qr_file}\n')

    return all_okay


def _file_header(prof: ProfileBase) -> str:
    """
    Top of config file
    """
    now = mod_time_now()
    ident = prof.ident

    title = '#\n'
    title += f'# vpn-name     : {ident.vpn_name}\n'
    title += f'# account-name : {ident.acct_name}\n'
    title += f'# profile-name : {ident.prof_name}\n'
    title += f'# is-gateway   : {prof.is_gw}\n'
    title += f'# date         : {now}\n'
    title += '#\n\n'

    return title


def _get_acct_dir(work_dir: str, vpn_name: str, acct_name: str) -> str:
    """
    Return (wg_dir, qr_dir) directories.
    If a problem they are empty
    """
    wg_dir = get_wg_vpn_dir(work_dir, vpn_name)
    if not make_dir_path(wg_dir):
        Msg.err(f'Error making dir {wg_dir}\n')
        return ''

    acct_dir = os.path.join(wg_dir, acct_name)

    return acct_dir


def _get_qr_dir(acct_dir: str) -> str:
    """
    Return qr_dir based on acct_dir.
    """
    qr_dir = os.path.join(acct_dir, 'qr')

    return qr_dir


def _wg_write_peer_gateways(wg_conf: WgConfigBase,
                            vpn_nets: list[str],
                            prof: ProfileBase,
                            alternate: bool) -> str:
    """
    Handle all the gateways for this config.
    Return data as a string to be written to config file.

    If alternate is true then return peer data only for
    alternate gateway peers. If no alternate peers, then
    no peers are returned
    """
    header = '#\n# Gateways\n#\n'
    data = ''

    if alternate and not prof.alternate_wanted:
        return data

    vpninfo = wg_conf.vpninfo
    wg_peer = WgPeerData()
    nets_shared = wg_conf.nets_shared
    id_str = prof.ident.id_str

    #
    # Sort accounts
    #
    x_acct_names: list[str] = []
    if wg_conf.gw_prof_names and len(wg_conf.gw_prof_names) > 0:
        x_acct_names = list(wg_conf.gw_prof_names.keys())
        if x_acct_names:
            x_acct_names.sort()

    for x_acct_name in x_acct_names:
        x_profiles = wg_conf.gw_prof_names[x_acct_name]

        for x_prof_name in x_profiles:
            x_prof = wg_conf.accts[x_acct_name].profile[x_prof_name]

            #  - exclude self or duplicate of self (same keys).
            if x_prof.ident.tag == prof.ident.tag:
                continue

            if x_prof.PrivateKey == prof.PrivateKey:
                continue

            # if alternates requested then skip if no alternate.
            if alternate and x_prof.ident.id_str not in wg_conf.gw_alternates:
                continue

            psk = vpninfo.psks.lookup_psk(prof.ident.tag, x_prof.ident.tag)

            x_id_str = x_prof.ident.id_str
            wg_peer.nets_common = nets_shared.get_common_nets(id_str, x_id_str)

            wg_peer.config_prof = prof
            wg_peer.prof = x_prof
            wg_peer.alternate = alternate
            wg_peer.psk = psk
            wg_peer.peer_to_peer = vpninfo.peer_to_peer
            wg_peer.vpn_nets = vpn_nets

            data += wg_peer.data()

    if data:
        data = header + data
    return data


def _wg_write_peer_clients(wg_conf: WgConfigBase, vpn_nets: list[str],
                           prof: ProfileBase) -> str:
    """
    If this config is a gateway, then add all the clients it supports.
    Return data as a string to be written to config file.
    """
    data = '\n#\n# Clients\n#\n'

    vpninfo = wg_conf.vpninfo
    wg_peer = WgPeerData()
    nets_shared = wg_conf.nets_shared
    id_str = prof.ident.id_str

    #
    # Sort
    #
    x_acct_names = []
    if wg_conf.cl_prof_names and len(wg_conf.cl_prof_names) > 0:
        x_acct_names = list(wg_conf.cl_prof_names.keys())
        if x_acct_names:
            x_acct_names.sort()

    for x_acct_name in x_acct_names:
        x_profiles = wg_conf.cl_prof_names[x_acct_name]

        for x_prof_name in x_profiles:
            x_prof = wg_conf.accts[x_acct_name].profile[x_prof_name]

            #  - exclude self
            if x_prof.ident.tag == prof.ident.tag:
                continue

            psk = vpninfo.psks.lookup_psk(prof.ident.tag, x_prof.ident.tag)

            x_id_str = x_prof.ident.id_str
            wg_peer.nets_common = nets_shared.get_common_nets(id_str, x_id_str)

            wg_peer.config_prof = prof
            wg_peer.prof = x_prof
            wg_peer.psk = psk
            wg_peer.peer_to_peer = vpninfo.peer_to_peer
            wg_peer.vpn_nets = vpn_nets
            wg_peer.alternate = False

            data += wg_peer.data()

    return data
