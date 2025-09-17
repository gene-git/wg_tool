# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Opts  - command line options for WgTool
"""
# pylint disable=too-many-instance-attributes
# pylint disable=too-many-statements
# pylint: disable=too-few-public-methods
import os
import sys

from utils import (Msg, version)
from data import get_top_dir

from ._opts_base import OptsBase
from .options import parse_args


class Opts(OptsBase):
    """
    Command line options
     - some may be optionally saved to file in config dir
    """
    def __init__(self):

        super().__init__()

        #
        # Map Command line options to attributes.
        # Note: may change work_dir.
        #
        option_dict = parse_args(self.work_dir, self.data_dir)
        if option_dict:
            for (key, val) in option_dict.items():
                setattr(self, key, val)
        if not self.work_dir:
            self.okay = False
            return

        #
        # Modify
        #
        if not _modify_check(self):
            self.okay = False
            return

        self.modify = bool(self.edit or self.merge or self.copy)
        self.modify |= bool(self.rename or self.new)
        self.modify |= bool(self.active or self.not_active)
        self.modify |= bool(self.hidden or self.not_hidden)
        self.modify |= bool(self.nets_wanted_add or self.nets_wanted_del)
        self.modify |= bool(self.nets_offered_add or self.nets_offered_del)

        #
        # ident_names is list of Identity names given on command line.
        # Command line must be of the form:
        #  vpn or vpn.acct or vpn.acct.prof where prof is a
        #  profile name or a comma separated list of profile names.
        #
        if self.ident_names:
            if not self.idents.parse_ids(self.ident_names):
                self.okay = False
                return
        #
        # validation checks
        #
        if not input_validation(self):
            self.okay = False
            return
        #
        # When requested, print version and exit
        #
        if self.version:
            vers = version() + '\n'
            Msg.plain(vers)
            sys.exit(0)

    def check(self):
        """
        consistency checks
        """
        if not self.work_dir:
            Msg.err('No work dir found. Unable to continue')
            return False

        if not os.path.isdir(self.work_dir):
            txt = f'({self.work_dir}). Unable to continue'
            Msg.err(f'work dir not a directory: {txt}')
            return False

        topdir = get_top_dir(self.work_dir)
        if not topdir:
            Msg.err(f'Top level dir not found {topdir}. Unable to continue')
            return False

        if not os.path.isdir(topdir):
            txt = f'({topdir}). Unable to continue'
            Msg.err(f'Top level dir not a directory: {txt}')
            return False

        return True


def input_validation(opts: OptsBase) -> bool:
    """
    Basic input validation checks
    - edit, copy, rename, require --ident
    - new: requires idents.ids
    """
    need_ident = bool(opts.edit or opts.copy or opts.rename)

    need_ids = bool(opts.new or opts.active or opts.not_active)
    need_ids |= bool(opts.roll_keys)
    need_ids |= bool(opts.hidden or opts.not_hidden)
    need_ids |= bool(opts.nets_wanted_add or opts.nets_wanted_del)
    need_ids |= bool(opts.nets_offered_add or opts.nets_offered_del)

    num_cl_parms = 0
    cl_parm = ''
    if opts.idents.ids:
        num_cl_parms = len(opts.idents.ids)
        cl_parm = opts.idents.ids[0].id_str

    if need_ident:
        if not opts.ident:
            Msg.warn('Missing --ident\n')
            if num_cl_parms == 1:
                Msg.plain(f'Using the positional ID instead {cl_parm}\n')
                opts.ident = cl_parm
            else:
                return False

    if need_ids:
        if num_cl_parms < 1:
            Msg.err('Missing command line ID(s) to create\n')
            return False

    # if self.nets_add and self.nets_del:
    #     txt = 'Error - cannot do both Add and Remove nets'
    #     Msg.err(f'Invalid options: {txt}\n')
    #     return False

    return True


def _modify_check(opts: Opts) -> bool:
    """
    Chack only 1 modify action requested at a time.
    """
    # bitfields
    flag: int = 1
    action_bits: dict[str, int] = {
            'edit': flag,
            'copy': flag << 1,
            'rename': flag << 2,
            'merge': flag << 3,
            'new': flag << 4,
            'nets_wanted_add': flag << 5,
            'nets_wanted_del': flag << 6,
            'nets_offered_add': flag << 7,
            'nets_offered_del': flag << 8
            }
    action: int = 0
    actions: int = 0

    #
    # Which action
    #
    for (act, bits) in action_bits.items():
        if getattr(opts, act):
            action = bits
            actions |= bits

    if actions == 0:
        # no actions.
        return True

    #
    # Check one action at a time.
    #
    if action & actions != action:
        ops = 'edit/merge/copy/rename/new/nets_wanted_add/nets_wanted_del'
        ops += '/nets_offered_add/nets_offered_del'
        Msg.err(f'Error: one of {ops}\n')
        Msg.plain(' Found:')
        for (act, bits) in action_bits.items():
            if bits & actions:
                Msg.plain(f' {act}')
        Msg.plain('\n')
        return False
    return True
