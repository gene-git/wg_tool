"""
When user doesn't specify then find work_dir by looking wlong the default work_path.

 - We could also check for config_dir/server/server.conf?
"""
import os

def check_work_dir_access(work_dir):
    """ check have rwx on work dir """
    dir_access = os.X_OK | os.R_OK | os.W_OK
    work_dir_access = os.access(work_dir, dir_access)
    return work_dir_access

def find_work_dir(init, work_path, config_dir):
    """
    When user doesn't specify then find work_dir using work_path.
    2 cases, init (no config dir) and normal case (needs config)

    A) init has been set:
        - if work_dir
            if rwx by user:
                return work_dir
        else
            try next in path
            else current dir (./)

    B) Normal (not init) :

        - if work_dir
            if rwx by user:
              if work_dir/config
                    ->  work_dir
        else
            try next in path

        if no config anywhere return './'
    """
    cwd = './'
    if not work_path:
        return cwd

    dir_access = os.X_OK | os.R_OK | os.W_OK
    #file_access = os.R_OK | os.W_OK

    work_dir = None
    wdir_list = work_path.split(':')
    for try_work_dir in wdir_list:
        # check if dir exists
        if not os.path.exists(try_work_dir):
            continue

        #
        # User has access
        #
        work_dir_access = os.access(try_work_dir, dir_access)
        if init:
            # Init case
            if work_dir_access:
                work_dir = try_work_dir
                break
        else:
            # normal case
            conf_dir = os.path.join(try_work_dir, config_dir)
            if not os.path.exists(conf_dir):
                continue

            config_dir_access = os.access(conf_dir, dir_access)
            if config_dir_access:
                work_dir = try_work_dir
                break

    if not work_dir:
        work_dir = cwd

    return work_dir
