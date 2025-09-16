# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Import one wireguard config file
"""
# pylint: disable = too-few-public-methods
# pylint: disable=duplicate-code
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-nested-blocks
from utils import Msg
from vpn import Vpn
from peers import Acct
from peers import Profile
from data import mod_time_now
from net import internet_networks
from net import cidr_in_cidrs

from .wg_conf_base import WgConfBase
from .gw_info import GwInfo
from .gw_infos import GwInfos


def import_one(vpn: Vpn, wg_conf: WgConfBase, gw_infos: GwInfos) -> bool:
    """
    Import wg_conf data into the vpn
    Each peer section encountered provides
    info about Endpoints and networks
    These are returned so caller can process them
        public-key: [networks, endpoint]
    """
    # sanity check
    if not _checks(vpn, wg_conf):
        return False

    #
    # Import the profile
    #
    now = mod_time_now()
    wg_interface = wg_conf.interface
    ident = wg_conf.ident

    acct_name = ident.acct_name
    if acct_name in vpn.accts:
        acct = vpn.accts[acct_name]
    else:
        acct = Acct(vpn.name, acct_name)
        acct.active = True
        acct.changed = True
        acct.mod_time = mod_time_now()
        vpn.accts[acct.name] = acct

    prof = Profile()
    prof.ident = ident
    prof.Address = wg_interface.Address
    prof.PrivateKey = wg_interface.PrivateKey
    prof.PublicKey = wg_interface.pubkey
    if not prof.PublicKey:
        Msg.err(f'Error importing {ident.id_str}\n')
        return False

    prof.pre_up = wg_interface.PreUp
    prof.pre_down = wg_interface.PreDown
    prof.post_up = wg_interface.PostUp
    prof.post_down = wg_interface.PostDown
    prof.dns = wg_interface.DNS
    prof.MTU = wg_interface.MTU

    prof.active = True
    prof.mod_time = now

    wg_dns = gw_infos.wg_dns
    gateway_config = False
    if wg_interface.ListenPort:
        #
        # gateway
        # - Save the gateway listen port.
        # - dont know if internet offered until parse
        #   peer AllowedIPs in pass 2
        # - dont know PersistentKeepalive until go thru all peers
        # - make a fake endpoint with port instead of host:port
        #
        gateway_config = True
        wg_dns.num_gw += 1
        prof.Endpoint = f'{wg_interface.ListenPort}'
        prof.internet_wanted = False
    else:
        #
        # client
        #
        wg_dns.num_cl += 1
    #
    # save any DNS this peer has
    # so pass 2 can find any commnon ones
    # that should be in vpninfo instead of profiles
    #
    if wg_interface.DNS:
        for host in wg_interface.DNS:
            if host not in wg_dns.dns:
                wg_dns.dns[host] = 0
            wg_dns.dns[host] += 1
    #
    # Check for keep-alive
    #
    for wg_peer in wg_conf.peers:
        if wg_peer.PersistentKeepalive:
            prof.PersistentKeepalive = wg_peer.PersistentKeepalive
            break

    #
    # Add profile to our vpn account
    #
    acct.profile[ident.prof_name] = prof

    #
    # update gateway info - prep for pass 2
    # A config is either a:
    #  - gateway config (interface plus peers)
    #    peer could be client info (no Endpoint)
    #    another gateway (has Endpoint)
    #  - client config (interface plus gateway peers)
    #    Every peer in this config has an Endpoint
    #    to allow it to connect to that gateway
    #
    # If a peer has an Endpoint - then:
    #   - Endpoint is to gateway
    #   - AllowedIPs are routes for client
    #     -> client nets_wanted
    #     -> gateway nets_offered.
    # We do not know the network topology, so user must
    # edit after import and confirm or correct nets_wanted/offered
    # if no Endpoint:
    #   - config is a gateway and this gateway gives
    #     permissions in AllowedIPs by this gateway.
    #     AllowedIPs -> nets_offered.
    # - pass 2 will check if vpn_nets uses /32 or /24
    #

    #
    # config interface pubkey
    #
    vpninfo = vpn.vpninfo
    internets = internet_networks()

    interface_pubkey = wg_interface.pubkey
    gw_info_config: GwInfo | None = None
    if wg_interface.ListenPort:
        pubkey = interface_pubkey
        if pubkey not in gw_infos.info:
            gw_infos.info[pubkey] = GwInfo()
        gw_info = gw_infos.info[pubkey]
        gw_info.pubkey = pubkey
        gw_info_config = gw_info

    #
    # Any AllowedIPs network seen in this peer
    # is assigned to both the config owner profile
    # and the peer seen in this config
    # i.e. Nets always connect a pair of peers
    #
    for wg_peer in wg_conf.peers:
        if wg_peer.Endpoint:
            endpoint = wg_peer.Endpoint
            # This peer connects to a gateway
            pubkey = wg_peer.PublicKey
            if pubkey not in gw_infos.info:
                gw_infos.info[pubkey] = GwInfo()
            gw_info = gw_infos.info[pubkey]

            if gw_info.pubkey and gw_info.pubkey != pubkey:
                Msg.err(' pubkey from interface and peer mismatch: ')
                Msg.plain(f'{gw_info.pubkey} vs {pubkey}\n')
                return False
            gw_info.pubkey = pubkey

            if gw_info.endpoint and endpoint != gw_info.endpoint:
                txt = f'pubkey is {pubkey} {endpoint} vs {gw_info.endpoint}'
                Msg.err(f'Error: Gateway with multiple endpoints: {txt}\n')
                return False
            gw_info.endpoint = endpoint

            if not gateway_config:
                # check if intetnet access wanted
                prof.internet_wanted = False
                for cidr in wg_peer.AllowedIPs:
                    if cidr in internets:
                        prof.internet_wanted = True
                        break

            for cidr in wg_peer.AllowedIPs:
                if vpninfo.networks.ip_is_subnet(cidr):
                    continue

                if gateway_config:
                    if not cidr_in_cidrs(cidr, gw_info.nets_offered):
                        gw_info.nets_offered.append(cidr)

                else:
                    if not cidr_in_cidrs(cidr, prof.nets_wanted):
                        prof.nets_wanted.append(cidr)

            #
            # psks
            # - are for every peer communicating with another peer
            # - we get from client conf (they are also in gateway conf)
            #
            if wg_peer.PresharedKey:
                tag = wg_conf.ident.tag
                gw_info.psks[tag] = wg_peer.PresharedKey

        if gateway_config and gw_info_config:
            gw_info = gw_info_config
            if wg_peer.AllowedIPs:
                for net in wg_peer.AllowedIPs:
                    if vpninfo.networks.ip_is_subnet(net):
                        if net not in gw_info.vpn_nets:
                            gw_info.vpn_nets.append(net)
                    else:
                        if not cidr_in_cidrs(net, gw_info.nets_offered):
                            gw_info.nets_offered.append(net)

    return True


def _checks(vpn: Vpn, wg_conf: WgConfBase) -> bool:
    """
    Check
    - vpn exists
    - profile does not exist
    """
    # vpn name
    if wg_conf.ident.vpn_name != vpn.name:
        Msg.err(f'vpn mismatch: {wg_conf.ident.vpn_name} vs {vpn.name}')
        return False

    # networks are in vpn
    nets_found = wg_conf.interface.Address
    networks = vpn.vpninfo.networks
    for net in nets_found:
        if not networks.is_address_available(net):
            Msg.err(f'Error: {wg_conf.file}\n')
            return False

    # no duplicate profile
    if vpn.acct_exists(wg_conf.ident):
        id_str = wg_conf.ident.id_str
        Msg.err(f'Duplicate: {id_str} already exists\n')
        return False
    return True
