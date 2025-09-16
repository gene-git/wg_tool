# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Hash a string
"""
from cryptography.hazmat.primitives import hashes


def message_digest(bdata: bytes) -> bytes:
    """
    Return sha384 hash of string.
    For human result.hex()
    We use newer SHA3 hash instead of SHA2
    """
    hashfunc = hashes.SHA3_384
    digest = hashes.Hash(hashfunc())
    digest.update(bdata)
    result = digest.finalize()
    return result
