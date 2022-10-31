"""
toml helper functions
    - NB toml write cannot handle None values
"""
import os
import sys
if sys.version_info >= (3,11):
    # 3.11 has tomllib 
    try:
        import tomllib as toml
    except ImportError:
        pass
else:
    import tomli as toml

import tomli_w
from .utils import open_file

def _dict_none_to_empty(dic):
    """
    Replaces None values with empty string ''
    returns copy of dictionary
    """
    clean = dic.copy()
    if not dic:
        return clean

    for key,val in clean.items():
        if not val:
            clean[key] = ''
        elif isinstance(val, dict):
            clean[key] = _dict_none_to_empty(val)

    return clean

def _dict_remove_none(dic):
    """
    Rmoves keys with None values
    returns copy of dictionary
    """
    clean = {}
    if not dic:
        return clean

    for key,val in dic.items():
        if not val:
            continue
        if isinstance(val, dict):
            new_val = _dict_remove_none(val)
            if new_val:
                clean[key] = new_val
        else:
            clean[key] = val

    return clean

def dict_to_toml_string(dic):
    """
    Returns a toml formatted string from a dictionary
      - Keys with None values are removed/ignored
    """
    clean_dict = _dict_remove_none(dic)
    txt = tomli_w.dumps(clean_dict)
    return txt

def read_toml_file(fpath):
    """
    read toml file and return a dictionary
    """
    this_dict = None
    if os.path.exists(fpath):
        fobj = open_file(fpath, 'r')
        if fobj:
            data = fobj.read()
            fobj.close()
            this_dict = toml.loads(data)
    return this_dict
