# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Create a new vpn/acct/profile
"""
from utils import Msg
from config import Opts
from ids import Identity
from vpn import Vpn

from .vpns_base import VpnsBase
from .modify_save import save_vpninfo_edit


def modify_new(vpns: VpnsBase) -> bool:
    """
    Create new item.
    Can be applied to vpn(s) or vpn.acct or vpn.acct.profile
    Required: All target id passed as positional
              parameters (opts.idents)
    Returrns True if all succeeded
    """
    #
    # IDs are passed in as positional parameters
    #
    opts = vpns.opts
    if not opts.idents.ids:
        return True

    #
    # Determine what needs to be done
    # new_vpns is list of requested new vpns
    # new_accts is {vpn_name: id_str, ...} for existing vpns
    # new_vpn_accts is same as new_accts but for vpns that dont exist
    #
    work = _Work()
    work.analyze(opts, vpns)

    #
    # Make New vpns (require editing for IPs etc)
    # Must first be created and edited before adding accts.
    #
    if work.new_vpns:
        if work.new_vpn_accts:
            Msg.err('Create new vpns first then add acct:profiles\n')
            Msg.plain('  Required to make vpn change first:\n')
            for (vpn_name, acctlist) in work.new_vpn_accts.items():
                Msg.plain(f'  {acctlist}\n')
            return False

        #
        # create the new vpns
        # save to edit dir - need IPs etc
        #
        for vpn_name in work.new_vpns:
            Msg.warn(f'Please add a gateway profile for {vpn_name}\n')
            vpn = Vpn(opts, vpn_name)
            vpns.vpn[vpn_name] = vpn

            if not save_vpninfo_edit(opts.work_dir, vpn.vpninfo):
                return False
    #
    # Make New accts
    #
    for (vpn_name, acctlist) in work.new_accts.items():
        vpn = vpns.vpn[vpn_name]

        gw_names = vpn.gateway_ids()
        if not gw_names:
            Msg.warnverb(f'Vpn {vpn_name} has no gateway.', level=2)
            Msg.warnverb(' Please add one.', level=2)

        for id_str in acctlist:
            ident = Identity()
            ident.from_str(id_str)

            prof = vpn.add_acct_prof(ident.acct_name, ident.prof_name)
            if not prof:
                return False
    return True


class _Work:
    """
    Identify what is to done
    """
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.new_vpns: list[str] = []
        self.new_accts: dict[str, list[str]] = {}
        self.new_vpn_accts: dict[str, list[str]] = {}

    def analyze(self, opts: Opts, vpns: VpnsBase):
        """
        Determine what needs to be done
        new_vpns is list of requested new vpns
        new_accts is {vpn_name: id_str, ...} for existing vpns
        new_vpn_accts is same as new_accts but for vpns that dont exist
        """

        for ident in opts.idents.ids:
            # Check for new vpn and any associated accts
            vpn_name = ident.vpn_name
            acct_requested = False
            if ident.acct_name or ident.prof_name:
                acct_requested = True

            if vpn_name not in vpns.vpn:
                # new vpn
                if vpn_name not in self.new_vpns:
                    self.new_vpns.append(vpn_name)

                if acct_requested:
                    if vpn_name not in self.new_vpn_accts:
                        self.new_vpn_accts[vpn_name] = []
                    self.new_vpn_accts[vpn_name].append(ident.id_str)

            elif acct_requested:
                # existing vpn + new acct(s)
                if vpn_name not in self.new_accts:
                    self.new_accts[vpn_name] = []
                self.new_accts[vpn_name].append(ident.id_str)

            else:
                # existing vpn no accts - nothing to do
                Msg.warn(f' New vpn skipped: {vpn_name} already exists\n')
