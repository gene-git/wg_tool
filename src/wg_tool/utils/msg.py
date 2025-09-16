# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Msg class for terminal messages.
simple message print
  - error
  - warn
  - header
todo: flip hdr <-> info: hdr->green, info->cyan
"""


class Msg:
    """
    Simple terminal message print
    * plain - no color
    * info -  green
    * hdr - cyan
    * warn - yellow
    * err - red
    * New line is suppressed - add where needed.
    """
    verb: int = 0

    @staticmethod
    def _msg_with_color(color: int, txt: str):
        """ print colored txt """
        esc = '\033['
        set_fg = '38;5;'
        set_off = '0'
        ctxt = f'{esc}{set_fg}{color}m{txt}{esc}{set_off}m'
        print(ctxt, end='')

    @staticmethod
    def plain(txt: str):
        """ print normal message (no color)"""
        print(txt, end='')

    @staticmethod
    def hdr(txt: str):
        """ print header (cyan)"""
        color = 51
        Msg._msg_with_color(color, txt)

    @staticmethod
    def warn(txt: str):
        """ print warning (yellow) """
        color = 11
        Msg._msg_with_color(color, txt)

    @staticmethod
    def err(txt: str):
        """ print error (red) """
        color = 196
        Msg._msg_with_color(color, txt)

    @staticmethod
    def info(txt):
        """ print info (green) """
        color = 10
        Msg._msg_with_color(color, txt)

    @staticmethod
    def plainverb(txt: str, level: int = 1):
        """ print normal message (no color)"""
        if Msg.verb >= level:
            Msg.plain(txt)

    @staticmethod
    def hdrverb(txt: str, level: int = 1):
        """ print normal message (no color)"""
        if Msg.verb >= level:
            Msg.hdr(txt)

    @staticmethod
    def warnverb(txt: str, level: int = 1):
        """ print normal message (no color)"""
        if Msg.verb >= level:
            Msg.warn(txt)

    @staticmethod
    def errverb(txt: str, level: int = 1):
        """ print normal message (no color)"""
        if Msg.verb >= level:
            Msg.err(txt)

    @staticmethod
    def infoverb(txt: str, level: int = 1):
        """ print normal message (no color)"""
        if Msg.verb >= level:
            Msg.info(txt)
