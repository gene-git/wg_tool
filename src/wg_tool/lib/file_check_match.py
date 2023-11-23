# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
conf_file_check
Before writing a file we check if current file has same content (aside from header).
This routine reads current file - strins header - and compares to the string about to be
written and returns true if they don't match
"""
import os
from .utils import open_file

def file_check_match(fpath, header, data_new):
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

    #
    # strip header lines
    # We ignore same number of chars - if number changes then header format changes
    # and its not a match
    #
    hdr_len = len(header)
    data = data[hdr_len:]

    if data == data_new:
        return matched

    return not matched
