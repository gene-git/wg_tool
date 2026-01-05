# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
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
    def msg(txt: str, fg: str = '', level: int = 0):
        """
        Message with foreground color support.
        """
        if level > Msg.verb:
            return

        if fg:
            esc = '\033['
            set_fg = '38;5;'
            set_off = '0'
            ctxt = f'{esc}{set_fg}{fg}m{txt}{esc}{set_off}m'
            print(ctxt, end='')
        else:
            print(txt, end='')

    @staticmethod
    def plain(txt: str, level: int = 0):
        """ print normal message (no color)"""
        Msg.msg(txt, level=level)

    @staticmethod
    def hdr(txt: str, level: int = 0):
        """ print header (cyan)"""
        Msg.msg(txt, fg='51', level=level)

    @staticmethod
    def warn(txt: str, level: int = 0):
        """ print warning (yellow) """
        Msg.msg(txt, fg='11', level=level)

    @staticmethod
    def err(txt: str, level: int = 0):
        """ print error (red) """
        Msg.msg(txt, fg='196', level=level)

    @staticmethod
    def info(txt, level: int = 0):
        """ print info (green) """
        Msg.msg(txt, fg='10', level=level)

    @staticmethod
    def plainverb(txt: str, level: int = 1):
        """ print normal message (no color)"""
        Msg.plain(txt, level=level)

    @staticmethod
    def hdrverb(txt: str, level: int = 1):
        """ print normal message (no color)"""
        Msg.hdr(txt, level=level)

    @staticmethod
    def warnverb(txt: str, level: int = 1):
        """ print normal message (no color)"""
        Msg.warn(txt, level=level)

    @staticmethod
    def errverb(txt: str, level: int = 1):
        """ print normal message (no color)"""
        Msg.err(txt, level=level)

    @staticmethod
    def infoverb(txt: str, level: int = 1):
        """ print normal message (no color)"""
        Msg.info(txt, level=level)
