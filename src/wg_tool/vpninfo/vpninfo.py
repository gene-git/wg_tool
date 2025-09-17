# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
'''
Each VPN shares same network space - IPv4 and IPv6.

All peers, clients and gateways, have their IP address(es)
in this network. These are the IPs used by wireguard itself.
They are not the Endpoint address.

Each gateway has some wg_address - which is an
address with host bits and a prefix. The network
is derived by setting the host bits to 0.

For example:
    10.10.10.100/24 => host 10.10.10.100, network = 10.10.10.0/24

 - ip and cidr: string(s)
 - addr ipa and net : are instances of ipaddress class

'''
# pylint disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
import os
from typing import Any

from py_cidr import Cidr

from utils import Msg
from utils import read_toml_file
from utils import dict_to_toml_string
from utils.debug import pprint

from ids import generate_tag
from psks import Psks
from data import (mod_time_now, get_vpninfo_file, write_dict)
from net import NetWorks


class VpnInfo:
    """
    Manage all IP addresses for a VPN network.

    VpnInfo is created whenever a vpn with unique name is created.
    The data is stored on disk (work-dir/data/gateways/<vpn-name>/Vpn.info
    """
    def __init__(self, work_dir: str, vpn_name: str):
        #
        # tag is used to ensure merge is for correct vpninfo.
        self.name: str = vpn_name
        self.tag: str = ''
        self.networks: NetWorks = NetWorks()

        #
        # peer_to_peer
        # true allows all peers to communicate with
        # one another. Changes gateway and all peers to have AllowedIPs
        # if entire vpn net not just point to point.
        #
        self.peer_to_peer: bool = False

        #
        # Create default vpn networks.
        #  - can be changed before adding peers.
        #
        vpn_nets = ['10.77.77.0/24', 'fc00:77:77::/64']
        for net_str in vpn_nets:
            self.networks.add_cidr(net_str)

        #
        # these are now per profile - no longer needed.
        # NB wireguard overloads dns for both dns and search domain.
        #    i.e. if DNS is IP its used for dns server,
        #         if non-IP then search domain
        # So see non-IP in dns list we lookup the IP
        # before writing to wireguard config
        #
        self.dns_script: str = '/etc/wireguard/scripts/wg-peer-updn'
        self.dns: list[str] = []
        self.dns_search: list[str] = []
        self.dns_lookup_ipv6: bool = False

        #
        # Below are all internal only (not editable)
        #
        self.dns_gateways: list[str] = []
        self.dns_search_gateways: list[str] = []
        self.mod_time: str = mod_time_now()
        self.active: bool = True
        self.hidden: bool = False

        #
        # Every pair of peers (one or both a gateway)
        # has a pre-shared secret key (PSK).
        #
        self.psks: Psks = Psks()

        self.okay: bool = True
        self.changed: bool = False

        # if Vpn.info file exists read it in.
        self.read_file(work_dir)

        # make sure we have a valid id tag
        if not self.tag:
            self.tag = generate_tag()
            self.changed = True

    def rename_vpn(self, vpn_name: str) -> bool:
        """
        vpn name change
        """
        if self.name != vpn_name:
            self.name = vpn_name
            self.changed = True
        return True

    def is_ready(self) -> bool:
        """
        Return true if enough information available
        Requires to be ready:
            Have network(s) defined (IP address(es)
            dns
        Optional:
            dns_search
        """
        net_strs = self.networks.get_net_strs()

        if not self.networks or not net_strs:
            Msg.warn('No vpn address(es)\n')
            return False

        if not self.dns:
            Msg.warn('No vpn dns servers\n')
            return False
        return True

    def put_dns_gateway(self, dns_gw: list[str], dns_search_gw: list[str]):
        """
        Update dns_gateways / dns_search_gatways
        """
        if set(self.dns_gateways) != set(dns_gw):
            self.changed = True
            self.dns_gateways = dns_gw

        if set(self.dns_search_gateways) != set(dns_search_gw):
            self.changed = True
            self.dns_search_gateways = dns_search_gw

    def get_cidrs(self) -> list[str]:
        """
        List of VPN networks in cidr string format
        """
        cidrs: list[str] = []
        if not self.networks:
            return cidrs

        cidrs = self.networks.get_net_strs()

        return cidrs

    def is_active(self) -> bool:
        """
        Return true if active else false
        """
        return self.active

    def set_active(self, is_active: bool):
        """
        Sets active flag to 'is_active'
        """
        if self.active == is_active:
            return

        self.active = is_active
        self.changed = True

    def is_hidden(self) -> bool:
        """
        Return true if hidden else false
        """
        return self.hidden

    def set_hidden(self, hidden: bool):
        """
        Sets hidden flag to 'hidden'
        """
        if self.hidden == hidden:
            return

        self.hidden = hidden
        if self.hidden:
            self.active = False
        self.changed = True

    def ip_in_vpn(self, cidr: str) -> bool:
        """
        Return True if ip is part of the vpn network.
        """
        if not cidr or not self.networks:
            return False

        is_subnet = self.networks.ip_is_subnet(cidr)
        return is_subnet

    def reset_cidrs(self, cidrs: list[str]):
        """
        Drop all existin networks and replace with cidrs.

        Only used in migration - never use anywhere else.
        """
        self.networks = NetWorks()
        self.add_cidrs(cidrs)

    def add_cidrs(self, cidrs: list[str]):
        """
        Defines the VPN network
        """
        self.changed = True
        for cidr in cidrs:
            cidr = Cidr.fix_cidr_host_bits(cidr)
            if not self.networks.add_cidr(cidr):
                Msg.err(f'Error initializing vpn {self.name} {cidr}')
                self.okay = False
                return

    def find_new_address(self) -> list[str]:
        """
        Returns list of new usable address strings for each of the
        networks in this vpn.
        """
        addresses: list[str] = []
        if not self.networks:
            return addresses

        addresses = self.networks.find_new_addresses()
        if not self.networks.okay:
            self.okay = False

        return addresses

    def is_address_available(self, cidr: str):
        """
        check if address (ip or cidr) is available
        """
        avail = self.networks.is_address_available(cidr)
        if avail:
            return True
        return False

    def mark_address_taken(self, cidrs: list[str]) -> bool:
        """
        Add cidr_str to list of used
        Must be in one of the known nets
        """
        if not cidrs:
            return True
        return self.networks.mark_addresses_taken(cidrs)

    def to_edit_dict(self) -> dict[str, Any]:
        """
        What we save in Edit file
        """
        data: dict[str, Any] = {}

        data['name'] = self.name
        data['tag'] = self.tag
        # data['allowed_ips'] = self.allowed_ips
        data['dns'] = self.dns
        data['dns_search'] = self.dns_search
        data['dns_lookup_ipv6'] = self.dns_lookup_ipv6
        data['peer_to_peer'] = self.peer_to_peer

        netlist: list[str] = self.networks.get_net_strs()
        if netlist:
            data['networks'] = netlist
        else:
            data['networks'] = ['10.77.77.0/24']

        return data

    def merge(self, attribs: dict[str, Any], has_profiles: bool) -> bool:
        """
        Merge user edits from dict.
        If vpn has profiles (using IPs) then has_profiles should
        be set to true. This prevents deleting the current
        network(s).
        """
        if not attribs:
            Msg.err('vpn info: No data provided to merge\n')
            return False

        tag = attribs.get('tag')
        if not tag or tag != self.tag:
            Msg.err('Error merge: bad tag: {self.tag} vs {tag}\n')
            return False

        name = attribs.get('name')
        if not name or name != self.name:
            Msg.err('Error merge: bad name: {self.name} vs {name}\n')
            return False

        # now do the merge
        if not self.from_dict(attribs, merging=True,
                              has_profiles=has_profiles):
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        """
        What we save in Vpn.info file
        """
        data: dict[str, Any] = {}

        data['name'] = self.name
        data['tag'] = self.tag
        data['dns'] = self.dns
        data['dns_search'] = self.dns_search
        data['dns_lookup_ipv6'] = self.dns_lookup_ipv6
        data['networks'] = []
        data['peer_to_peer'] = self.peer_to_peer
        # data['psks'] = self.psks.to_dict()

        netlist: list[str] = self.networks.get_net_strs()
        if netlist:
            data['networks'] = netlist

        data['dns_gateways'] = self.dns_gateways
        data['dns_search_gateways'] = self.dns_search_gateways
        data['mod_time'] = self.mod_time
        data['active'] = self.active
        data['hidden'] = self.hidden
        return data

    def from_dict(self,
                  data: dict[str, Any],
                  merging: bool = False,
                  has_profiles: bool = True) -> bool:
        """
        Load from saved Vpn.info file
        """
        #
        # Checks
        #
        if not data:
            Msg.warn('VpnInfo: No data passed in')
            return False

        name = data.get('name')
        if name and name != self.name:
            Msg.err('Err: Vpn.info has wrong vpn name')
            Msg.plain(f' {name} vs {self.name}')
            self.okay = False
            return False

        okay = _from_dict(self, data, merging, has_profiles)
        return okay

    def read_file(self, work_dir: str) -> bool:
        """
        Read from Vpn.info
        """
        vpn_name = self.name
        info_file = get_vpninfo_file(work_dir, vpn_name)
        if not os.path.isfile(info_file):
            return False

        info_dict = read_toml_file(info_file)
        if not info_dict:
            Msg.err('VpnInfo: Error reading Vpn.info file\n')
            self.okay = False
            return False

        if not self.from_dict(info_dict, merging=False, has_profiles=False):
            Msg.err('VpnInfo: Error parsing Vpn.info file\n')
            self.okay = False
            return False

        if not self.psks.read_file(work_dir, vpn_name):
            self.okay = False
            return False

        return True

    def write_file(self, work_dir: str, tag_map: dict[str, str]) -> bool:
        """
        Write to Vpn.info
        Args:
            work_dir (str):
                The work dir everyhing lives under

            tag_map (dict[str, str]):
                Map tag -> peer_id string
        """
        #
        # Vpn Info
        #
        vpn_name = self.name
        info_file = get_vpninfo_file(work_dir, vpn_name)

        file = os.path.basename(info_file)
        info_dict = self.to_dict()
        if not info_dict:
            Msg.err('VpnInfo: Error generating data dictionary\n')
            self.okay = False
            return False

        title = vpn_name
        (ok, changed) = write_dict(title, info_dict, info_file, footer='')
        if not ok:
            Msg.err('VpnInfo: Error writing Vpn.info file\n')
            self.okay = False
            return False
        if changed:
            Msg.info(f'  {file} updated\n')

        #
        # Psks Info
        #
        footer = _psk_footer(self.psks, tag_map)
        if not self.psks.write_file(work_dir, vpn_name, footer):
            self.okay = False
            return False
        return True

    def for_edit_file(self) -> str:
        """
        Write to fpath
        Args:
            fpath (str):
                File to create with editable merge file
        """
        # file = os.path.basename(fpath)
        # Msg.info(f'  {file}\n')
        info_dict = self.to_edit_dict()
        if not info_dict:
            Msg.err('VpnInfo: Error generating data dictionary\n')
            self.okay = False
            return ''

        title = f'# {self.name}\n'
        title += '# vpn info\n'
        title += '# Required: vpn cidr block(s):\n'
        title += '#   networks = ["10.77.77.0/24", "fc00:77.77::/64"]\n'
        title += '# Required: dns server(s) host(s) and/or ip(s)\n'
        title += '#   dns = ["dns1.example.com", "10.1.1.1"]\n'
        title += '# Do not change the name or tag fields.\n'
        title += '# Other fields are optional.\n'
        title += '#\n'

        info_str = title
        info_str += dict_to_toml_string(info_dict, drop_empty=False)

        return info_str

    def pprint(self, recurs: bool = False):
        """ pretty print self """
        pprint(self, recurs=recurs)


def _psk_footer(psks: Psks, tag_map: dict[str, str]) -> str:
    """"
    psks use tags which are not user friendsly.
    Add footer to bottom of vpninfo file which uses
    ids instead
    """
    footer: str = '\n#\n# PSK by peer_name:prof_name pairs\n#\n'

    for (ident, psk) in psks.psk.items():
        id_tags = ident.split('+')
        id1 = tag_map.get(id_tags[0])
        id2 = tag_map.get(id_tags[1])

        if not id1:
            id1 = id_tags[0]
            Msg.warn(f' tag map missing {id1}\n')
        if not id2:
            id2 = id_tags[1]
            Msg.warn(f' tag map missing {id2}\n')

        item = f'# {psk:45s} = {id1:30s} x {id2:30s}\n'
        footer += item
    return footer


def _from_dict(vpninfo: VpnInfo,
               data: dict[str, Any],
               merging: bool = False,
               has_profiles: bool = True) -> bool:
    """
    Load from saved Vpn.info file
    """
    # pylint: disable=too-many-branches
    Msg.infoverb('Vpninfo: load from dictionary\n', level=2)

    tag = data.get('tag')
    if tag and tag != vpninfo.tag:
        Msg.plainverb(f' updating tag: {tag}\n', level=2)
        vpninfo.tag = tag

    dns = data.get('dns')
    if dns and isinstance(dns, list):
        if set(dns) != set(vpninfo.dns):
            Msg.plainverb(f' updating dns: {dns}\n', level=2)
            vpninfo.dns = dns

    dns_search = data.get('dns_search')
    if dns and isinstance(dns_search, list):
        if set(dns_search) != set(vpninfo.dns_search):
            Msg.plainverb(f' updating dns_search: {dns_search}\n', level=2)
        vpninfo.dns_search = dns_search

    dns_lookup_ipv6 = data.get('dns_lookup_ipv6')
    if isinstance(dns_lookup_ipv6, bool):
        if dns_lookup_ipv6 != vpninfo.dns_lookup_ipv6:
            Msg.plainverb(f' updating dns_lookup_ipv6: {dns_lookup_ipv6}\n',
                          level=2)

    dns = data.get('dns_gateways')
    if dns and isinstance(dns, list):
        if set(dns) != set(vpninfo.dns_gateways):
            Msg.plainverb(f' updating dns_gateways: {dns}\n', level=2)
            vpninfo.dns_gateways = dns

    dns_search = data.get('dns_search_gateways')
    if dns and isinstance(dns_search, list):
        if set(dns_search) != set(vpninfo.dns_search_gateways):
            txt = f' updating dns_search_gatwways: {dns_search}'
            Msg.plainverb(f'{txt}\n', level=2)
        vpninfo.dns_search_gateways = dns_search

    peer_to_peer = data.get('peer_to_peer')
    if peer_to_peer is not None:
        if peer_to_peer != vpninfo.peer_to_peer:
            vpninfo.peer_to_peer = peer_to_peer

    #
    # We must check if cidr is in an existing networks
    # or if cidr is a supernet of existing networks
    # Simplest to create a new class NetWorks to hold
    # all the networks and do the work to "merge" or add
    # any network.
    #
    net_strs = data.get('networks')
    if not merging or not has_profiles:
        vpninfo.networks = NetWorks()

    if net_strs and isinstance(net_strs, list):
        for net_str in net_strs:
            vpninfo.networks.add_cidr(net_str)

    if merging:
        return True
    #
    # These are not used for merging edit files
    # Only for database reads
    #
    # psks_dict = data.get('psks')
    # if psks_dict and isinstance(psks_dict, dict):
    #    vpninfo.psks.from_dict(psks_dict)

    item = data.get('mod_time')
    if item and isinstance(item, str):
        vpninfo.mod_time = item

    flag = data.get('active')
    if flag and isinstance(flag, bool):
        vpninfo.active = flag

    flag = data.get('hidden')
    if flag and isinstance(flag, bool):
        vpninfo.hidden = flag
    return True
