# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Create a new vpn/acct/profile
"""
# pylint: disable=duplicate-code
# pylint: disable=too-many-return-statements
import os
from typing import Any

from utils import Msg
from utils import read_toml_file

from .vpns_base import VpnsBase
from .modify_save import get_prof_save_file
from .modify_save import get_vpninfo_save_file
from .tag_to_vpn_prof import tag_to_vpn_prof


def modify_merge(vpns: VpnsBase) -> bool:
    """
    Edit can be:
        vpn -> vpninfo handles
        vpn.acct.profile
    Nothing to edit for vpn.acct

    Returrns True if all succeeded
    """
    Msg.info('Mod merge:\n')

    #
    # ID to edit is passed as opts.ident
    #
    opts = vpns.opts

    #
    # merge file content
    #
    (tag, what, data) = _merge_file_content(opts.work_dir, opts.merge)
    if not (tag and what):
        Msg.err('Merge file invalid\n')
        return False

    #
    # Lookup who tag belongs to
    #  - either vpn or profile or neithr
    #
    (vpn, prof) = tag_to_vpn_prof(vpns, tag)

    if what == 'vpn':
        #
        # vpn
        #
        if not vpn:
            Msg.err('Merge vpn info: unknown vpn tag {tag}\n')
            return False

        has_profiles = vpn.has_any_profiles()
        vpninfo = vpn.vpninfo
        if not vpninfo.merge(data, has_profiles):
            Msg.err('Merge vpn: failed\n')
            return False

    elif what == 'prof':
        #
        # profile
        #
        if not prof:
            Msg.err(f'Merge profile: unknown tag {tag}\n')
            return False

        if not prof.merge(data):
            Msg.err('merge profile: Failed\n')
            return False
    else:
        # bad file or file content
        return False

    return True


def _merge_file_content(work_dir: str, file: str
                        ) -> tuple[str, str, dict[str, Any]]:
    """
    Read merge file and return content as dictionary
    along with the content type.

    Returns:
        (tag: str, content_type: str, content: dictionary)

        content_type is one of 'vpn', 'prof' or ''
        empty string means unknown file content
    """
    #
    # Check file exists
    #
    content: dict[str, Any] = {}
    content_type = ''
    tag = ''
    if not file:
        return (tag, content_type, content)

    if not os.path.isfile(file):
        Msg.err(f'Merge file not found: {file}\n')
        #
        # if file is an ID instead of file
        #
        guess = _locate_merge_file(work_dir, file)
        if guess:
            Msg.plain(f'  Did you mean: {guess}\n')
        return (tag, content_type, content)

    #
    # Read it
    #
    content = _read_merge_file(file)
    if not content:
        Msg.err('Merge - nothing found in file\n')
        return (tag, content_type, content)

    content_type = _merge_data_type(content)
    if not content_type:
        Msg.err('Merge - unknown merge file content\n')
        return (tag, content_type, content)

    #
    # Find the tag
    #
    tag_key = 'tag'
    match content_type:
        case 'vpn':
            # is variable in content dictionary
            if tag_key in content:
                tag = content[tag_key]
            else:
                Msg.err('Merge - vpn file missing tag\n')

        case 'prof':
            ident_key = 'ident'
            if ident_key in content and tag_key in content[ident_key]:
                tag = content[ident_key][tag_key]
            else:
                Msg.err('Merge - profile file missing tag\n')
        case _:
            Msg.err('Merge: unknown content in file\n')

    return (tag, content_type, content)


def _read_merge_file(file: str) -> dict[str, Any]:
    """
    Read the file and return as dictionary.
    """
    data_dict = read_toml_file(file)
    if not data_dict:
        Msg.err(f'Mod Merge - empty or missing merge file: {file}\n')
    return data_dict


def _merge_data_type(info_dict: dict[str, Any]) -> str:
    """
    Determine if the merge file content is for
    vpn or for profile.

    Use key:
     - vpn has 'networks'
     - profile has 'ident'

    Returns:
        'vpn' if vpninfo
        'prof' if profile
        '' if unknown
    """
    if not info_dict:
        return ''

    if 'networks' in info_dict:
        return 'vpn'

    if 'ident' in info_dict:
        return 'prof'

    return ''


def _locate_merge_file(work_dir: str, name: str) -> str:
    """
    If name passed in was ID not file path try find it.
    """
    if not name:
        return ''

    if '.' in name:
        file = get_prof_save_file(work_dir, name)
        if os.path.isfile(file):
            return file
    else:
        file = get_vpninfo_save_file(work_dir, name)
        if os.path.isfile(file):
            return file
    return ''
