# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
 Generate wireguard user config and QR code for all users
   - don't limit to active users that only affects server config
"""
# pylint disable=C0103,R0914,R1732
import os

from .file_tools import setup_save_path
from .file_tools import save_prev_symlink
from .file_tools import file_symlink
from .file_tools import format_file_header
from .utils import open_file
from .utils import text_to_qr_file
from .file_check_match import file_check_match

def _user_prof_str(wgtool, _user_name, _prof_name, profile):
    """
    Generate one users profile as a string ready to write
    """
    server = wgtool.server

    serv_PublicKey = server.PublicKey

    PrivateKey = profile.PrivateKey
    Address = profile.Address
    PresharedKey = profile.PresharedKey
    AllowedIPs = profile.AllowedIPs
    Endpoint = profile.Endpoint

    prof = '\n'
    prof += '[Interface]\n'
    prof += f'{"PrivateKey":15s} = {PrivateKey}\n'
    prof += f'{"Address":15s} = {Address}\n'

    if profile.DnsLinux:
        # linux we manage resolv.conf
        dns_updn_script = wgtool.dns_updn_script
        args = ''
        if profile.DnsSearch and server.DNS_SEARCH:
            args += ' -dnsrch ' + ','.join(server.DNS_SEARCH)
        args += ' -dns ' + ','.join(server.DNS)

        prof += f'{"Postup":15s} = {dns_updn_script} -u{args}\n'
        prof += f'{"PostDown":15s} = {dns_updn_script} -d\n'

    else:
        # non-linux or linux with wg-quick/resolvconf
        if profile.DnsSearch and server.DNS_SEARCH:
            dns_items = server.DNS + server.DNS_SEARCH
        else:
            dns_items = server.DNS
        for dns in dns_items:
            prof += f'{"DNS":15s} = {dns}\n'

    prof += '\n'
    prof += '[Peer]\n'

    prof += f'{"PublicKey":15s} = {serv_PublicKey}\n'
    if PresharedKey:
        prof += f'{"PresharedKey":15s} = {PresharedKey}\n'

    prof += f'{"AllowedIPs":15s} = {AllowedIPs}\n'

    prof += f'{"Endpoint":15s} = {Endpoint}\n'
    prof += '\n'
    return prof

def write_wg_users(wgtool):
    """
    write out all wg user configs in 'user_name' directory :
      - config_name.conf, config_name.qr.png
      - see README for directory / file structure
    """
    # pylint: disable=R0914,C0301
    errors = 0
    msg = wgtool.msg
    vmsg = wgtool.vmsg
    emsg = wgtool.emsg

    # require DNS
    if not wgtool.server.DNS:
        emsg('Error: Server missing DNS')
        msg('  No user wg configs saved')
        errors += 1
        return errors


    topdir = wgtool.wg_users_dir

    for user_name,user in wgtool.users.items() :
        user_dir = os.path.join(topdir, user_name)

        for (prof_name, profile) in user.profile.items():
            prof_str = _user_prof_str(wgtool, user_name, prof_name, profile )

            #
            # file names - since user files may be shared etc - we keep file name unique
            # i.e. in <user>/<user>-<config>.conf - even tho looks duplicative
            # we still want separate dir per user
            #
            if prof_name == user_name :
                base_name = f'{user_name}'
            else:
                base_name = f'{user_name}-{prof_name}'

            conf_file = f'{base_name}.conf'
            (actual_file, link_name, link_targ) = setup_save_path(wgtool, user_dir, conf_file, mkdirs=False)

            comment = f' wg profile :\n# {"User":>10s} {user_name}\n# {"Profile":>10s} {prof_name}'
            header = format_file_header(comment, wgtool.now)

            is_same = file_check_match(link_name, header, prof_str)
            if is_same:
                vmsg(f'{"wg-config":>10s}: up to date - {user_name}:{prof_name}')
            else:
                (actual_file, link_name, link_targ) = setup_save_path(wgtool, user_dir, conf_file, mkdirs=True)
                msg(f'{"wg-config":>10s}:   updating - {user_name}:{prof_name}')
                fobj = open_file(actual_file, 'w')
                if fobj:
                    fobj.write(header)
                    fobj.write(prof_str)
                    save_prev_symlink(user_dir, link_name)
                    file_symlink(link_targ, link_name)
                else:
                    emsg(f'Error writing user wg config {actual_file}')
                    errors += 1

                # QR code file
                qr_file = f'{base_name}-qr.png'
                (actual_file, link_name, link_targ) = setup_save_path(wgtool, user_dir, qr_file)
                okay = text_to_qr_file(prof_str, actual_file,)
                if okay:
                    save_prev_symlink(user_dir, link_name)
                    file_symlink(link_targ, link_name)
                else:
                    emsg(f'Error writing user wg QR code {actual_file}')
                    errors += 1
    return errors
