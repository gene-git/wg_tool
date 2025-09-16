# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Wireguard uses these configs
"""
# pylint: disable=too-few-public-methods

from utils import Msg
from config import Opts
from vpninfo import VpnInfo

from .wg_config_base import WgConfigBase
from .acct import Acct
from .wg_write import wg_write_config


class WgConfig(WgConfigBase):
    """
    Each profile has it's own wireguard config has 2 kinds of sections
     - [Interface]
     - [Peer]
    There is one interface and one or more peer sections.
    See wireguard docs and man pages for wg and wg-quick

    This class is used to generate them.
    """
    def __init__(self, opts: Opts, vpninfo: VpnInfo, accts: dict[str, Acct]):

        super().__init__(opts, vpninfo, accts)

        if not accts:
            return

        if not opts.brief:
            Msg.info('  Wireguard configs\n')

        _init_helpers(self)
        _init_dns(self)
        _init_gw_alternates(self)

    def write_all(self) -> bool:
        """
        For each profile, create and write out it's wireguard config.
        Return True all being well.
        """
        # Have any profiles?
        if not self.prof_names:
            return True

        status = True
        acct_names = self.acct_names
        prof_names = self.prof_names

        for acct_name in acct_names:
            if not prof_names[acct_name]:
                continue

            for prof_name in prof_names[acct_name]:
                okay = wg_write_config(self, acct_name, prof_name)
                if not okay:
                    status = False
        return status


def _init_gw_alternates(wg_conf: WgConfig):
    """
    Make list of ID strings of gateways with an
    alternate Endpoint.
    """
    gw_alternates: list[str] = []
    for (acct_name, prof_names) in wg_conf.gw_prof_names.items():
        for prof_name in prof_names:
            prof = wg_conf.accts[acct_name].profile[prof_name]
            if prof.Endpoint_alt:
                gw_alternates.append(prof.ident.id_str)
    wg_conf.gw_alternates = gw_alternates


def _init_dns(wg_conf: WgConfig):
    """
    Gather up all the dns information. Dns servers and search domains
    come from, in order:
    - profile
      Profile dns is prepended as each profile is processed.
    - gateways
    - vpninfo
    """
    #
    # Gateways dns
    #
    for (acct_name, prof_names) in wg_conf.gw_prof_names.items():
        for prof_name in prof_names:
            prof = wg_conf.accts[acct_name].profile[prof_name]
            if prof.dns:
                wg_conf.dns += prof.dns

            if prof.dns_search:
                wg_conf.dns_search += prof.dns_search

    #
    # Vpn dns
    #
    if wg_conf.vpninfo.dns:
        wg_conf.dns += wg_conf.vpninfo.dns

    if wg_conf.vpninfo.dns_search:
        wg_conf.dns_search += wg_conf.vpninfo.dns_search


def _init_helpers(wg_conf: WgConfig):
    """
    Build the helpers.
     - acct_names, prof_names,
     - wg_prof_names, cl_prof_names
     - gw_nets_offered, cl_nets_offered
    """
    for (acct_name, acct) in wg_conf.accts.items():
        if not acct.active:
            continue

        wg_conf.acct_names.append(acct_name)

        (gw_names, cl_names) = acct.active_profile_names()

        wg_conf.prof_names[acct_name] = gw_names + cl_names
        if gw_names:
            wg_conf.gw_prof_names[acct_name] = gw_names

        if cl_names:
            wg_conf.cl_prof_names[acct_name] = cl_names

        # (gw_id_str, cl_id_str) = acct.active_profile_id_str()

        for prof_name in wg_conf.prof_names[acct_name]:
            prof = acct.profile[prof_name]
            id_str = prof.ident.id_str

            if prof.nets_wanted:
                wg_conf.nets_shared.add_wanted_by(id_str, prof.nets_wanted)

            if prof.nets_offered:
                wg_conf.nets_shared.add_offered_by(id_str, prof.nets_offered)

    #
    # refresh
    # - determines if any cidr is subnet of another
    # - update nets_by_peers and peers_by_nets
    #
    wg_conf.nets_shared.refresh()
