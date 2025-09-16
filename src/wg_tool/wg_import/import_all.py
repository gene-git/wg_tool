# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Import wg configs
"""
from utils import Msg
from vpn import Vpn

from .filenames import files_to_import
from .gw_infos import GwInfos
from .wg_conf import WgConf


def import_all_wg_configs(vpn: Vpn) -> bool:
    """
    Import standard wireguard configs.
    - vpn must have matching name and networks
    - Configs must use our ID directory hierarch
      <vpn>/<account>/<profile>.conf

    Pass 1:
    Import each profile.
    Each file that is imported returns the peer information it found
    as list of WgConfPeers.

    Pass 2
    Use wg peer info to update gateway info:
        publickey -> gateway
        allowed_ips -> vpn ip (is it /32 or /24 -> peer_to_peer)
                    -> nets_allowed (remove vpn net from here)
        if every peer uses same dns move it to vpninfo.dns, or gateway dns
        psk(id1, id2) -> psks

    So return the wg_conf.peers to caller
    WHen hit Endpoint in a peer - then find WgConfInterface with same privkey
    and check it's ListenPort matches the Endpoint
    """
    Msg.info('Importing configs\n')
    work_dir = vpn.opts.work_dir
    vpn_name = vpn.name

    if not vpn_name or not vpn.vpninfo.networks.nets:
        Msg.err('Error: vpn must be created before import\n')
        return False

    # get files to import
    files = files_to_import(work_dir, vpn_name)
    if not files:
        Msg.warn('Warn: No configs found\n')
        return True

    #
    # Phase 1:
    #   import each profile.
    #
    # wg_conf_list: list[WgConf] = []
    gw_infos = GwInfos()
    for file in files:
        Msg.plain(f'  loading {file}\n')
        wg_conf = WgConf()
        if not wg_conf.load_wg_conf_file(file):
            return False

        if not wg_conf.import_one(vpn, gw_infos):
            return False

    #
    # Phase 2:
    #  - update gateways from peer.Endpoint, peer.AllowedIPs
    #
    Msg.plain('  analyzing\n')
    if not gw_infos.update_gateways(vpn):
        return False

    #
    # Ask user to check nets_offered/wanted
    #
    Msg.hdr('\nImport completed\n')
    Msg.info('\n\nPlease confirm / correct nets_wanted and nets_offered\n')
    Msg.plain('Run : wg-tool -lv\n')
    Msg.plain('Correct any using *--edit vpn.acct.profile*\n')
    Msg.plain('or with *--nets-wanted-add <id>* and *--nets-wanted-del <id>\n')
    Msg.plain('   and similarly for *offered*\n')
    return True
