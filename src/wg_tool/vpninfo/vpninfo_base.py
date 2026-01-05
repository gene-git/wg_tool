# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
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
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

from wg_tool.utils.debug import pprint

# from ids import generate_tag
from wg_tool.psks import Psks
from wg_tool.data import (mod_time_now)
from wg_tool.net import NetWorks


class VpnInfoBase:
    """
    Base Class to Manage IP networks/addresses for a VPN network.

    VpnInfo is created whenever a vpn with unique name is created.
    The data is stored on disk (work-dir/data/<vpn-name>/Vpn.info
    """
    def __init__(self, vpn_name: str):
        #
        # tag is used to ensure merge is for correct vpninfo.
        self.name: str = vpn_name
        self.tag: str = ''
        self.networks: NetWorks = NetWorks()

        #
        # To help with data changes we keep a version
        # Empty version => toml
        # Version: 1 => yaml and includes newer NetWorks with group / subnets
        #
        self.version: str = '1'

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
        # self.read_file(work_dir)

        # make sure we have a valid id tag
        # if not self.tag:
        #     self.tag = generate_tag()
        #     self.changed = True

    def pprint(self, recurs: bool = False):
        """ pretty print self """
        pprint(self, recurs=recurs)
