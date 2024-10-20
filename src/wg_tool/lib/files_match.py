# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Before writing a file we check if current file has same content (aside from header).
This routine reads current file - strins header - and compares to the string about to be
written and returns true if they don't match
"""
import os
from crypto import message_digest
from .utils import open_file

def files_match(fpath, header, data_new):
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
    # Ignore header size bytes - note that if header size changes then header format changes
    # and wont match
    #
    hdr_len = len(header)
    data = data[hdr_len:]

    if len(data) != len(data_new):
        return not matched

    #
    # They match if the message_digests match
    # digest is sha3-384 (strong hash)
    #
    if message_digest(data.encode('utf-8')) == message_digest(data_new.encode('utf-8')):
        return matched

    return not matched
