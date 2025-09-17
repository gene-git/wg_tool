# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Text tool(s)
"""
from typing import Generator


def csv_string_to_list(txt: str) -> list[str]:
    """
    wg uses 2 ways to have list of items.
    (a) "a, b, c, ... "
    (b) repeated key = values

    This parses (a) and returns of strings
    """
    tlist: list[str] = []
    if not txt:
        return tlist

    tlist = txt.split(',')
    tlist = [item.strip() for item in tlist]
    return tlist


def list_string_to_csv_sublists(items: list[str], num: int) -> list[str]:
    """
    Given list of strings, return a new list where each element
    is a comman separated string with up to num (of the original) elements

    E.g.
        ['a', 'b', 'c', 'd', 'e'] -> ['a, b, c', 'd, e']
    """
    csv_list: list[str] = []
    if not items:
        return csv_list

    for sublist in _yield_chunk(items, num):
        if len(sublist) > 1:
            csv_sublist = ', '.join(sublist)
        else:
            csv_sublist = sublist[0]
        csv_list.append(csv_sublist)

    return csv_list


def _yield_chunk(items: list[str], num: int
                 ) -> Generator[list[str], list[str], None]:
    """
    Yield successive list of num-elem chunks out of items list
    """
    for i in range(0, len(items), num):
        yield items[i:i + num]
