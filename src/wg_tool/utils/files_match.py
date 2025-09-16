# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Tool to check if 2 files are the same.

Before writing a file check if file has
same content.

If strip_comments is true then any line starting
with a '#' is ignored in the comparison.

Logic:
Read current file - if asked then strips comments/header rows,
compare to the data about to be
written and return true if they match

"""
import os
from crypto import message_digest

from .read_write import open_file
from .comments import clean_comments


def files_match(fpath: str, data_new: str,
                strip_comments: bool = False) -> bool:
    """
    Read 'fpath' - remove header - compare to data_new
    Returns True if they are the same
    """
    matched = True
    if not os.path.exists(fpath):
        return not matched

    fobj = open_file(fpath, 'r')
    if fobj:
        data = fobj.read()
        fobj.close()
    else:
        return not matched

    if not data:
        return not matched

    # strip comments
    data_clean: str
    data_new_clean: str
    if strip_comments:
        data_clean = clean_comments(data)
        data_new_clean = clean_comments(data_new_clean)
    else:
        data_clean = data
        data_new_clean = data_new

    if len(data_clean) != len(data_new_clean):
        return not matched

    #
    # They match if the message_digests match
    # digest used at time of writing is sha3-384 (strong hash)
    #
    data_hash = message_digest(data_clean.encode('utf-8'))
    data_new_hash = message_digest(data_new_clean.encode('utf-8'))

    if data_hash == data_new_hash:
        return matched
    return not matched
