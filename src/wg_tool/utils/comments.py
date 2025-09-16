# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Clean up text
"""


def clean_comments(data: str, ok_comments: list[str] | None = None) -> str:
    """
    Examine data line by line.
    Any empty line or lines starting with '#' are dropped.
    Any line with comment after data has the comment part removed.

    Lines are then put back into string and returned.
    """
    clean: str = ''
    if not data:
        return clean

    rows: list[str] = data.splitlines()
    for row in rows:
        row = clean_comment(row, ok_comments)
        if row:
            clean += row + '\n'
    return clean


def clean_comment(row: str, ok_comments: list[str] | None = None) -> str:
    """
    CLean whitespace + comments from text string.
    Comment row containing words in the keep list are not dropped.
    Comments that comes after data is always ignored.
    """
    keepers: list[str] = []
    if ok_comments is not None:
        keepers = ok_comments

    clean = row.strip()

    # drop empty lines
    if not clean or clean[0] in ('\n'):
        return ''

    # drop comments on their own line unless a keeper
    if clean[0] in ('#'):
        if keepers and _keep_comment(clean, keepers):
            return clean
        return ''

    # data - check if comments after data to be dropped
    vrow = clean.split('#', 1)
    if keepers and len(vrow) > 1:
        if _keep_comment(vrow[1], keepers):
            return clean
    clean = vrow[0].strip()
    return clean


def _keep_comment(data: str, keepers: list[str]) -> bool:
    """
    Return true if data contains a comment to keep.
    """
    if not keepers:
        return False

    if any(item in data for item in keepers):
        return True
    return False
