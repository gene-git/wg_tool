# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Debuging tools

In order to get full support (with recursion)
add class method pprint() to class.
"""
from typing import Any

from .msg import Msg


def pprint(this: Any, recurs: bool = False):
    """
    Print class attributes (skip dunders)
    """
    if not _is_class(this):
        Msg.warn('Not an instance of a class\n')
        return

    Msg.info(f'{this.__class__.__name__} instance:\n')
    for (attr, val) in vars(this).items():
        if not attr.startswith('__'):
            Msg.plain(f'{attr:>15s}: ')

            if isinstance(val, dict):
                _dict_print(val, recurs)

            elif recurs and _is_class(val) and _has_method(val, 'pprint'):
                # attribute is a class => recurse if asked & possible.
                Msg.plain('\n')
                val.pprint(recurs=recurs)
            else:
                Msg.plain(f'{val}\n')


def _is_class(this: Any) -> bool:
    """
    Returns true if this is an instance of class
    """
    try:
        getattr(this, '__dict__')
    except AttributeError:
        return False
    return True


def _has_method(this: Any, method: str) -> bool:
    """
    Return True if this is instance of
    class and has  method 'method';
    """
    if not _is_class(this):
        return False

    if hasattr(this, method):
        if callable(getattr(this, method)):
            return True
    return False


def _dict_print(adic: dict[str, Any], recurs: bool):
    """
    Display dictionary
    """
    Msg.hdr('Dictionary:\n')
    for (key, val) in adic.items():
        Msg.plain(f'\n\t{key:>15s}: ')

        if recurs and _is_class(val) and _has_method(val, 'pprint'):
            Msg.plain('\n')
            val.pprint(recurs=recurs)
        else:
            Msg.plain(f' "{val}"\n')
