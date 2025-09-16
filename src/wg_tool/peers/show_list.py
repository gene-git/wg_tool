# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Profile
"""
# pylint: disable=too-many-branches
from utils import Msg
from utils import state_marker
from config import Opts

from .profile_base import ProfileBase


def show_list(prof: ProfileBase, opts: Opts):
    """
    Display profile on one line with no newline.
    vpn caller does line breaks
    """
    brief = opts.brief
    verb_level = opts.verb

    # skip dead profiles unless verbose is on level 2
    if prof.hidden and not verb_level >= 2:
        return

    if brief:
        id_str = prof.ident.id_str
        Msg.plain(f'{"":20s} {id_str:20s}\n')
        return

    state_mark = state_marker(prof.hidden, prof.active)
    mod_time = prof.mod_time
    name = prof.ident.prof_name
    is_gw = ' (gateway)' if prof.is_gw else ''
    has_alt = ' [Has Alt]' if prof.alternate_wanted else ''
    Msg.plain(f'{"":20s} {state_mark} {name:20s} {mod_time}{is_gw}{has_alt}\n')

    #
    # nets
    #
    if verb_level > 0:
        internet = ['internet']

        if prof.nets_offered or prof.internet_offered:
            nets = prof.nets_offered.copy()
            if prof.internet_offered:
                nets += internet
            value = f'{nets}'
            Msg.plain(f'{"":20s} {"nets_offered":>20s} : {value}\n')

        if prof.nets_wanted or prof.internet_wanted:
            nets = prof.nets_wanted.copy()
            if prof.internet_wanted:
                nets += internet
            value = f'{nets}'
            Msg.plain(f'{"":20s} {"nets_wanted":>20s} : {value}\n')

    if verb_level < 2:
        return

    Msg.plain(f'{"":20s} {"Address":>20s} : {prof.Address}\n')
    Msg.plain(f'{"":20s} {"PublicKey":>20s} : {prof.PublicKey}\n')
    # Msg.plain(f'{"":20s} {"AllowedIPs":>20s} : {prof.AllowedIPs}\n')

    if prof.PersistentKeepalive > 0:
        keepalive = f'{prof.PersistentKeepalive}'
        Msg.plain(f'{"":20s} {"PersistentKeepalive":>20s} : {keepalive}\n')

    if prof.MTU:
        Msg.plain(f'{"":20s} {"MTU":>20s} : {prof.MTU}\n')

    if prof.Endpoint:
        Msg.plain(f'{"":20s} {"Endpoint":>20s} : {prof.Endpoint}\n')

    # txt = prof.internet_offered
    # Msg.plain(f'{"":20s} {"internet_offered":>20s} : {txt}\n')

    # txt = prof.internet_wanted
    # Msg.plain(f'{"":20s} {"internet_wanted":>20s} : {txt}\n')

    if prof.dns_linux:
        Msg.plain(f'{"":20s} {"dns_linux":>20s} : {prof.dns_linux}\n')

    # if prof.DnsSearch:
    #     Msg.plain(f'{"":20s} {"DnsSearch":>20s} : {prof.DnsSearch}\n')

    if prof.dns_postup:
        Msg.plain(f'{"":20s} {"dns_postup":>20s} : {prof.dns_postup}\n')

    if prof.dns_postdn:
        Msg.plain(f'{"":20s} {"dns_postdn":>20s} : {prof.dns_postdn}\n')

    if prof.post_up:
        Msg.plain(f'{"":20s} {"PostUp":>20s} : {prof.post_up}\n')

    if prof.post_down:
        Msg.plain(f'{"":20s} {"PostDown":>20s} : {prof.post_down}\n')
