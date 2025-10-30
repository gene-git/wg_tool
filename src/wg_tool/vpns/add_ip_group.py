# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Add IP Group to vpn network
"""
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches

from utils import Msg
from ids import Identity
from data import mod_time_now

from .vpns_base import VpnsBase


def add_vpn_ip_group(vpns: VpnsBase) -> bool:
    """
    Handle
    - add_ip_group_name to vpn
    Add ip group to specified vpn. Vpn must exist.
    """
    opts = vpns.opts
    if not opts.add_ip_group_name or not opts.ident:
        return True

    group_name = opts.add_ip_group_name
    subnets = opts.add_ip_group_subnets

    ident = Identity()
    ident.from_str(opts.ident)
    vpn_name = ident.vpn_name

    if vpn_name not in vpns.vpn:
        Msg.err(f'vpn {vpn_name} not found\n')
        return False

    vpn = vpns.vpn[vpn_name]
    vpninfo = vpn.vpninfo

    if not vpninfo.add_ip_group(group_name, subnets):
        return False
    return True


def add_profile_ip_group(vpns: VpnsBase) -> bool:
    """
    Handle:
    - add ip_group and allow_ip_groups to peer profile(s).
    - Group(s) must exist.
    - Profile must exit (--new handles group for new profile)
    """
    opts = vpns.opts
    if not (opts.ip_group or opts.allow_ip_groups):
        return True

    group_name: str = ''
    group_names: list[str] = []
    if opts.ip_group:
        group_name = opts.ip_group
        group_names += [group_name]

    allow_groups: list[str] = []
    if opts.allow_ip_groups:
        allow_groups = opts.allow_ip_groups
        group_names += allow_groups

    #
    # Check group name in each vpn once
    #
    vpn_checked: list[str] = []

    for ident in opts.idents.ids:
        vpn_name = ident.vpn_name

        #
        # checks
        #
        acct_name = ident.acct_name
        prof_name = ident.prof_name
        if not prof_name:
            Msg.err('ip group needs peer profile name\n')
            return False

        if vpn_name not in vpns.vpn:
            Msg.err(f'ip group unkown vpn: {vpn_name}\n')
            return False

        vpn = vpns.vpn[vpn_name]
        vpninfo = vpn.vpninfo

        #
        # Check group name(s) exist
        #
        if vpn_name not in vpn_checked:
            vpn_checked.append(vpn_name)
            for name in group_names:
                if not vpninfo.has_ip_group(name):
                    Msg.err(f'ip group {name} not in {vpn_name}\n')
                    return False
        #
        # add ip group to profile.
        # - check profile ip not already in ip group
        # - get new ip from group ips
        # - update profile
        #
        (acct, prof) = vpn.find_acct_prof(acct_name, prof_name)
        if not (acct and prof):
            Msg.err(f' ip group: {group_name} Needs full Id with vpn.acct.profile\n')
            return False

        if group_name and prof.ip_group == group_name:
            Msg.warn(f'{prof_name} already in group {group_name}\n', level=1)

        changed: bool = False
        if group_name:
            #
            # check if profile ip(s) part of group
            #
            has_group_ip: bool = False
            for ip in prof.Address:
                group_name_check = vpninfo.networks.ip_to_group_name(ip)
                if group_name_check and group_name_check == group_name:
                    Msg.warn(f'{prof_name} already has {ip} in {group_name}\n')
                    has_group_ip = True

            if not has_group_ip:
                #
                # we dont check every vpn net has group - should never happen
                # change profile ips to group ips
                #
                Msg.msg(f'  {prof_name} changing to ip group {group_name}\n')
                prof.ip_group = group_name
                prof.Address = vpninfo.find_new_address(group=group_name)
                changed = True

        for name in allow_groups:
            if name not in prof.allow_ip_groups:
                changed = True
                prof.allow_ip_groups.append(name)
                prof.internet_wanted = False

        if changed:
            prof.changed = True
            prof.mod_time = mod_time_now()

    return True
