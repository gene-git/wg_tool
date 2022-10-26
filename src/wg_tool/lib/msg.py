"""
simple message print
  - error
  - warn
"""
def _msg_col(color, txt, end=None):
    """ print colored txt """
    esc = '\033['
    set_fg = '38;5;'
    set_off = '0'
    ctxt = f'{esc}{set_fg}{color}m{txt}{esc}{set_off}m'
    print(ctxt, end=end)

def hdr_msg(txt, end=None):
    """ print heaer (cyan)"""
    col = 51
    _msg_col(col, txt, end=end)

def warn_msg(txt, end=None):
    """ print warning (yellow) """
    col = 11
    _msg_col(col, txt, end=end)

def err_msg(txt, end=None):
    """ print error (red) """
    col = 196
    _msg_col(col, txt, end=end)
