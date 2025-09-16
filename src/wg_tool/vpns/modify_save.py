# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Edits save into file - user modifies and merges file.
This handles that file.

   <edit-dir>/<vpn-name>/vpn-info.mods
                        /Profiles/<id>.mods

<edit-dir> ~ <work-dir>/Edits See data module.
"""
import os

from utils import Msg
from utils import write_path_atomic
from data import get_edit_dir
from peers import Profile
from vpninfo import VpnInfo


def get_vpninfo_save_file(work_dir: str, vpn_name: str):
    """
    Return path to vpninfo save file
     - workdir/Edits/<vpn_name>-info.mods
    """
    edit_file = f'{vpn_name}-info.mods'
    edit_dir = get_edit_dir(work_dir)
    edit_path = os.path.join(edit_dir, edit_file)
    return edit_path


def get_prof_save_file(work_dir: str, id_str: str) -> str:
    """
    Return path to profile save file
     - workdir/Edits/<id>.mods
    """
    edit_file = f'{id_str}.mods'
    edit_dir = get_edit_dir(work_dir)
    edit_path = os.path.join(edit_dir, edit_file)
    return edit_path


def save_prof_edit(work_dir: str, prof: Profile) -> bool:
    """
    Write profile edit file.
    Returns True if all well.
    """
    id_str = prof.id_string()

    edit_path = get_prof_save_file(work_dir, id_str)

    title = '#\n'
    title += f'# Identity: {id_str}\n'
    title += '#\n'
    title += '# After edits, merge changes using\n'
    title += f'#\twg-tool --merge "{edit_path}"\n'
    title += '#\n'
    title += '# Do NOT change any part of "ident".\n'
    title += '#\n'

    pstr = title
    pstr += prof.for_edit()

    Msg.plain('Saving edit file. If desired, edit to modify any info.')
    Msg.plain('File saved to:\n')
    Msg.plain(f'\t"{edit_path}"\n')
    Msg.plain('Merge changes using\n')
    Msg.plain(f'\twg-tool --merge "{edit_path}"\n')

    if not write_path_atomic(pstr, edit_path, save_prev=True):
        return False
    return True


def save_vpninfo_edit(work_dir: str, vpninfo: VpnInfo) -> bool:
    """
    Write vpninfo edit file.
    Once changes/edits are ready, "--merge <file>"
    Returns True if all well.
    """
    vpn_name = vpninfo.name
    edit_path = get_vpninfo_save_file(work_dir, vpn_name)

    title = '#\n'
    title += f'# vpninfo: {vpn_name}\n'
    title += '#\n'
    title += '# After edits, merge changes using\n'
    title += f'#\twg-tool --merge "{edit_path}"\n'
    title += '#\n'

    pstr = title
    pstr += vpninfo.for_edit_file()

    Msg.plain(f'Saving edit file to : {edit_path}\n')
    Msg.plain('Please edit: add dns server(s). Optionally adjust IPs.\n')
    Msg.plain(f'Then --merge {edit_path} to incorporate your changes\n')

    if not write_path_atomic(pstr, edit_path, save_prev=True):
        return False
    return True
