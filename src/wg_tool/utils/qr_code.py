# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
wg-tool support utils`

"""
import os
import qrcode

from .comments import clean_comments
from .msg import Msg
from .file_tools import make_dir_path
from .file_tools import os_chmod


def text_to_qr_file(data: str, qr_fname: str, fmode: int = -1) -> bool:
    """
    make qr code from txt and write to file
    - any exception / error handling needed?

    Image file type is based on extension.
    If not specified png is used which makes the smallest file size.
    Supported types are those provided by pillow save()
    """
    if not qr_fname:
        return True

    # make directory to qr file if needed.
    if not _dir_make(qr_fname):
        return False

    qr_err = qrcode.constants.ERROR_CORRECT_H      # L M Q H
    qr: qrcode.QRCode = qrcode.QRCode(
            version=None,
            error_correction=qr_err,
            box_size=20,
            border=2,
            )

    txt = clean_comments(data)
    qr.add_data(txt)
    try:
        qr.make(fit=True)
    except ValueError as exc:
        Msg.warn(f'QR Generation error {exc}\n')
        return False

    fg = 'black'
    bg = 'white'
    img = qr.make_image(fill_color=fg, back_color=bg)

    (_base, ext) = os.path.splitext(qr_fname)
    ext = ext.replace('.', '')

    try:
        img.save(qr_fname, ext)
    except PermissionError:
        return False

    if fmode > 0 and not os_chmod(qr_fname, fmode):
        Msg.warn(f'Warning : failed to set file permissions {qr_fname}\n')
    return True


def _dir_make(fname) -> bool:
    """
    Ensure directory is available.
    """
    dirname = os.path.dirname(fname)
    if not make_dir_path(dirname):
        return False
    return True
