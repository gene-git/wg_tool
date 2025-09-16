# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Migrate legacy to new format

- configs/server/server.conf
  ->
  Data/vpn1/
            Vpn.info
            servers/hostname.prof

- configs/users/<user>/<user.conf>
  ->
  Data/vpn1/<user>/profile1.conf
                   profile2.conf etc
"""
# pylint: disable=too-many-locals, too-many-statements
import uuid

from py_cidr import Cidr

from utils import Msg
from data import mod_time_now
from config import Opts

from vpns import Vpns
from vpn import Vpn
from vpninfo import VpnInfo
from net import internet_networks
from net import cidr_in_cidrs

from peers import Acct
from peers import Profile

from ids import Identity

from .server import Server
from .users import Users
from .user import User
# from .migrate_int import migrate_internal


def migrate_server(vpn: Vpn) -> tuple[Identity, list[str]]:
    """
    Migrate legacy server to new data
    Update vpn, for gateway
    Returns server ident and list of active users
    """
    Msg.hdr(' server:\n')
    work_dir = vpn.opts.work_dir
    serv = Server(work_dir)

    # set vpn network(s)
    # vpninfo keeps the network prefix
    vpn.vpninfo = VpnInfo(work_dir, vpn.name)
    vpninfo = vpn.vpninfo

    #
    # We dont want the default vpn networks.
    # Going to take whatever is in the existing config
    #
    vpninfo.reset_cidrs(serv.Address)
    vpninfo.dns = serv.DNS
    vpninfo.dns_search = serv.DNS_SEARCH

    # acct + 1 profile
    acct_name = 'servers'
    Msg.plain(f'   {acct_name}\n')

    if acct_name in vpn.accts:
        acct = vpn.accts[acct_name]
    else:
        acct = Acct(vpn.name, acct_name)
        acct.active = True
        acct.changed = True
        acct.mod_time = mod_time_now()
        vpn.accts[acct.name] = acct

    prof = Profile()
    ident = prof.ident

    ident.vpn_name = vpn.name
    ident.acct_name = acct.name

    prof_name = _choose_server_profile_name(vpn, ident)
    ident.prof_name = prof_name
    ident.new_tag()
    ident.refresh()

    #
    # Old configs overloaded network prefix with vpn prefix
    # We need to set the prefix in profile back to 32, 128
    #
    prof.Address = _usable_ip_addresses(vpninfo, serv.Address)

    prof.PrivateKey = serv.PrivateKey
    prof.PublicKey = serv.PublicKey
    prof.post_up = [serv.PostUp]
    prof.post_down = [serv.PostDown]
    prof.internet_offered = True
    prof.internet_wanted = False

    # old way had no way to allow internal nets for servers
    # only for users which is weirdly lacking
    # prof.nets_offered = serv.AllowedIPs

    prof.active = True

    endpoint = f'{serv.Hostname}:{serv.ListenPort}'
    prof.Endpoint = endpoint
    if serv.Hostname_Int or serv.ListenPort_Int:
        endpoint_alt = f'{serv.Hostname_Int}:{serv.ListenPort_Int}'
        prof.Endpoint_alt = endpoint_alt
        Msg.warn(f'Alternate Endpoint: {endpoint_alt}.\n')
        Msg.warn('Please edit any profile that should have an')
        Msg.warn(' additional wireguard config using it\n')
        Msg.warn(' by setting: alternate_wanted = true\n')

    prof.changed = True
    prof.mod_time = mod_time_now()

    acct.profile[ident.prof_name] = prof

    return (ident, serv.active_users)


def migrate_users(vpn: Vpn, serv_ident: Identity,
                  active_users: list[str]) -> list[str]:
    """
    Migrate legacy users to new data
    """
    Msg.hdr(' users:\n')
    work_dir = vpn.opts.work_dir
    users = Users(work_dir)

    nets_all: list[str] = []
    for user in users.data:
        Msg.plain(f'   {user.name}:\n')
        active = bool(user.name in active_users)
        nets = migrate_user(user, serv_ident, active, vpn)
        for net in nets:
            if not cidr_in_cidrs(net, nets_all):
                nets_all.append(net)

    # should no longer be needed
    nets = list(set(nets))
    return nets


def migrate_user(user: User, srv_ident: Identity, active: bool,
                 vpn: Vpn) -> list[str]:
    """
    migrate on legacy user to new
    User is mapped to a acct and
    each legacy profile is mapped to 1 new profile.
    Returns list of networks for all profiles seen
    """
    internets = internet_networks()
    nets_seen: list[str] = []

    #
    # User -> acct
    #
    srv_tag = srv_ident.tag
    srv_acct_name = srv_ident.acct_name
    srv_prof_name = srv_ident.prof_name

    (_srv_acct, srv_prof) = vpn.find_acct_prof(srv_acct_name, srv_prof_name)

    if not srv_prof:
        Msg.err(f'Error: no server profile : {srv_ident.id_str}\n')
        return nets_seen

    active_profiles = user.active_profiles
    acct = Acct(vpn.name, user.name)

    # acct.name = user.name
    # acct.vpn_name = vpn.name
    acct.changed = True
    acct.active = active
    acct.mod_time = mod_time_now()
    vpn.accts[acct.name] = acct
    vpninfo = vpn.vpninfo
    psks = vpninfo.psks

    #
    # profiles
    #
    Msg.plain('     profiles:\n')
    for (prof_name, prof) in user.profile.items():
        Msg.plain(f'       {prof_name}\n')
        profile = Profile()
        ident = profile.ident

        ident.vpn_name = vpn.name
        ident.acct_name = acct.name
        ident.prof_name = prof_name
        ident.new_tag()
        ident.refresh()

        #
        # Some legacy profiles have no psk - we dont want to
        # break existing configs by adding missing psk
        # so we mark this acct as not using psk.
        # If this legacy prfile has no psk, we mark the
        # (tag, srv_tag) as no_psk pairs. Same with srv_int_tag
        #
        psk = prof.PresharedKey
        if psk:
            psks.put_shared_key(srv_tag, ident.tag, psk)
        else:
            profile.no_psk_tags.append(srv_tag)

        profile.Address = _usable_ip_addresses(vpninfo, prof.Address)
        profile.PrivateKey = prof.PrivateKey
        profile.PublicKey = prof.PublicKey

        #
        # Networks
        #   - internet_wanted => internet_offered by the gw
        #   - nets = make list of all client AllowedIPs
        #       These are associated with this profile as well as
        #       the gateway.
        #   - once we have them all, parse into named groups
        #     if net is used by all clients add to "net0"
        #     otherwise "net1" list of clients (id_str)
        #     install named net groups into gateway.
        #     For net0 (all) every profile gets nets_wanted "net0"
        #     profiles get whatever they asked for but now by "name"
        #
        profile.internet_wanted = False
        for cidr in prof.AllowedIPs:
            if cidr in internets:
                profile.internet_wanted = True
                continue

            if not cidr_in_cidrs(cidr, nets_seen):
                nets_seen.append(cidr)

            if not cidr_in_cidrs(cidr, profile.nets_wanted):
                profile.nets_wanted.append(cidr)

        profile.PersistentKeepalive = prof.PersistentKeepalive
        profile.dns_linux = prof.DnsLinux
        profile.internet_offered = False

        if prof_name in active_profiles:
            profile.active = True
        else:
            profile.active = False

        profile.changed = True
        profile.mod_time = mod_time_now()

        acct.profile[prof_name] = profile
    return nets_seen


def migrate_data(opts: Opts) -> bool:
    """
    Migrate legacy data to new
    """
    #
    # create Vpn
    #
    vpn_name = 'vpn1'
    Msg.info(f'Data migration begins to vpn: {vpn_name}\n')

    #
    # create Vpns
    #
    vpns = Vpns(opts)
    vpn = Vpn(opts, vpn_name)
    vpns.vpn[vpn_name] = vpn

    #
    # add server to it
    #
    (serv_ident, active_users) = migrate_server(vpn)
    srv_aname = serv_ident.acct_name
    srv_pname = serv_ident.prof_name
    (_srv_acct, srv_prof) = vpn.find_acct_prof(srv_aname, srv_pname)
    if not srv_prof:
        # should not happen
        Msg.err(f'Error - missing server: {serv_ident.id_str}\n')
        return False

    #
    # now users
    # - nets_asked: network: list[(acct, prof)] having it in AllowedIPs
    #   e.g. "a.b.c.d/24": [id1, id2, ...]
    #   Each network gets a name and is added to
    #   gateway prof.nets_shared {name1: list[nets], name2: list[nets]
    #   client profiles then get prof.nets_shared_wanted = [name1, ...]
    #
    srv_prof.nets_offered = migrate_users(vpn, serv_ident, active_users)

    #
    # Now all users(clients)/server(gateway) are migrated (with their IPs)
    # write them out
    #

    vpns.write()

    Msg.info('\nData migrated. Run "wg-tool -lv" to check the status\n')

    return True


def _usable_ip_addresses(vpninfo: VpnInfo, ips: list[str]) -> list[str]:
    """
    Check ip(s) are available
    If not get new ones
    """
    new_ips: list[str] = []
    for addr in ips:
        # get address with prefix  /32 or /128
        ip = Cidr.ip_to_address(addr)
        net = Cidr.cidr_to_net(str(ip))
        cidr = str(net) if ip else ''
        if cidr and vpninfo.is_address_available(cidr):
            vpninfo.mark_address_taken([cidr])
            new_ips.append(cidr)
        else:
            new_ips += vpninfo.find_new_address()
            Msg.warn(f' IP unavailable : "{ip}" -> {new_ips}\n')

    if new_ips:
        new_ips = list(set(new_ips))
    else:
        Msg.warn('migrate: No usable IPs found\n')
    return new_ips


def _choose_server_profile_name(vpn: Vpn, ident: Identity) -> str:
    """
    Simple algo to choose server profile name
    Unlikely to be name clash but be careful anyway
    """
    counter = 0
    acct_name = ident.acct_name
    root = 'wg'
    while counter < 10:
        name = f'{root}{counter}'
        (_acct, prof) = vpn.find_acct_prof(acct_name, name)
        if not prof:
            return name
        counter += 1

    prof_name = root + str(uuid.uuid4())[0:6]

    return prof_name
