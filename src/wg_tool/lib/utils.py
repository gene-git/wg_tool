# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
wg-tool support utils`
"""
# pylint: disable=invalid-name
import os
from datetime import datetime
import qrcode

def text_to_qr_file(txt, qr_fname):
    """
    make qr code from txt and write to file
        - any exception / error handling needed?
    """
    okay = True
    qr_err = qrcode.constants.ERROR_CORRECT_Q      # L M Q H
    qr = qrcode.QRCode(version=None,
                       error_correction=qr_err,
                       box_size=20,
                       border=4,
                       )

    qr.add_data(txt)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_fname)
    return okay

def current_date_time_str (fmt='%Y%m%d-%H:%M:%S'):
    """
    date time string
    """
    today = datetime.today()
    today_str = today.strftime(fmt)
    return today_str

def file_date_time_str(file, fmt='%y%m%d-%H:%M'):
    """ return mod time of file """
    mod_time = os.path.getmtime(file)
    dtime = datetime.fromtimestamp(mod_time)
    mod_time_str = dtime.strftime(fmt)
    return mod_time_str

def open_file(path, mode):
    """
    Open a file and return file object
    """
    # pylint: disable=W1514,R1732
    try:
        fobj = open(path, mode)
    except OSError as err:
        print(f'Error opening file {path} : {err}')
        fobj = None
    return fobj
