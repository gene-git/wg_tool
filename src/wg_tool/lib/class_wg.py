"""
  wg-tool base class

    Tool to administer wireguard users and server config with key management
    Driven from 2 types of simple input configs - 1) server.conf and per user.conf
"""
# pylint: disable=R0902,C0301
import os
from .class_wgtopts import WgtOpts

from .config_init import initial_server_config
from .utils import current_date_time_str

from .read_config import read_server_config, read_user_configs
from .write_config import write_server_config, write_user_configs
from .wg_users import write_wg_users
from .wg_server import write_wg_server
from .find_user_ip import find_user_ip

from .users import add_users
from .key_change import upd_user_keys
from .key_change import upd_serv_keys
from .users import add_active_users_profiles
from .users import remove_active_users_profiles
from .users import list_users

from .import_user import import_user

from .msg import hdr_msg, warn_msg, err_msg

from .cleanup import cleanup

class WgtServer:
    """
    Our server info
    """
    # pylint: disable=R0903
    def __init__(self, serv_dict):
        self.active_users = None
        self.Address = None
        self.Hostname = None
        self.Hostname_Int = None
        self.ListenPort = None
        self.ListenPort_Int = None
        self.PrivateKey = None
        self.PublicKey = None
        self.PostUp = None
        self.PostDown = None
        self.DNS = None

        for key, val in serv_dict.items():
            setattr(self, key, val)

    def __getattr__(self,name) :
        return None

    def to_dict(self):
        """" return dict of self """
        serv_dict = vars(self)
        return serv_dict

    def endpoint(self):
        """ return endpoint for user config """
        Endpoint = f'{self.Hostname}:{self.ListenPort}'
        return Endpoint

    def endpoint_int(self):
        """ return internal endpoint for user config """
        if self.ListenPort_Int:
            Endpoint = f'{self.Hostname}:{self.ListenPort_Int}'
        else:
            Endpoint = f'{self.Hostname}:{self.ListenPort}'
        return Endpoint

    def user_allowedips(self):
        """ return default AllowedIPs for user config """
        return '0.0.0.0/0'

    def add_active_user(self, user_name):
        """ add user to active_users list (user exists check in wgtool """
        if self.active_users:
            if user_name not in self.active_users:
                self.active_users.append(user_name)
        else :
            self.active_users = [user_name]

    def remove_active_user(self, user_name):
        """ remove user from active_users list """
        changed = False
        if self.active_users:
            if user_name in self.active_users:
                self.active_users.remove(user_name)
                changed = True
        return changed

    def is_user_active(self, user_name):
        """ check if user_name is active """
        if self.active_users:
            return bool(user_name in self.active_users)
        return False

class WgtUserProfile:
    """
    Users can have 1 or more Items - each has separate access (phone, laptop etc)
    """
    # pylint: disable=R0902,R0903
    def __init__(self, _prof_name, prof_dict):
        self.Address = None
        self.PrivateKey = None
        self.PublicKey = None
        self.PresharedKey = None
        self.AllowedIPs = None
        self.Endpoint = None

        for key,val in prof_dict.items():
            setattr(self, key, val)

    def __getattr__(self,name) :
        return None

    def to_dict(self):
        """ return dict of self """
        prof_dict = vars(self)
        return prof_dict

class WgtUser:
    """
    one user -
      - active_configs : list
      - config : dictionary of each config (instance of WgtUserItem)
    """
    # pylint: disable=R0902,R0903
    def __init__(self, user_name, user_dict):
        self.active_profiles = []
        self.profile = {}
        self.changed = False

        self.name = user_name
        for key,val in user_dict.items():
            if isinstance(val, dict):
                prof_name = key
                prof_dict = val
                self.profile[prof_name] = WgtUserProfile(prof_name, prof_dict)
            else:
                setattr(self, key, val)

    def __getattr__(self,name) :
        return None

    def refresh_active_profiles(self):
        """ refresh active_profiles - remove any if profile missing """

        if not self.active_profiles:
            return

        if not self.profile:
            self.changed = True
            self.active_profiles = None
            return

        active_profiles = []
        for prof_name in self.active_profiles:
            if self.profile_exists(prof_name):
                if prof_name not in active_profiles:
                    active_profiles.append(prof_name)
            else:
                self.changed = True
        self.active_profiles = active_profiles

    def profile_names(self):
        """ return list of elem names """
        prof_names = []
        if self.profile:
            for prof_name, _prof_class in self.profile.items():
                prof_names.append(prof_name)
        return prof_names

    def to_dict(self):
        """ return dict of self """
        user_dict = {'name' : self.name,
                     'active_profiles' : self.active_profiles,
                     }
        if self.profile:
            for prof_name, prof_class in self.profile.items():
                prof_dict = prof_class.to_dict()
                user_dict[prof_name] = prof_dict
        return user_dict

    def profile_exists(self, prof_name):
        """ check if profile exists """
        if self.profile:
            return bool(prof_name in self.profile)
        return False

    def is_profile_active(self, prof_name):
        """ check if profile is active """
        if self.active_profiles :
            return bool(prof_name in self.active_profiles)
        return False

    def add_profile(self, prof_name, prof_dict):
        """
        add new profig
          - add to active_profiles as well
        """
        if self.profile_exists(prof_name):
            warn_msg(f'{self.name} : profile {prof_name} already exists')
        else:
            self.profile[prof_name] = WgtUserProfile(prof_name, prof_dict)
            self.add_active_profile(prof_name)
            self.changed = True

    def add_active_profile(self, prof_name):
        """ add profile to users active_profile list """
        changed = False
        if self.profile_exists(prof_name):
            if self.active_profiles:
                if prof_name not in self.active_profiles:
                    self.active_profiles.append(prof_name)
                    changed = True
            else :
                self.active_profiles = [prof_name]
                changed = True
        else:
            warn_msg(f'Config {prof_name} not found - not added to active_profiles')
        return changed

    def remove_active_profile(self, prof_name):
        """ remove profile from users active_profile list """
        changed = False
        if self.profile_exists(prof_name):
            if self.active_profiles:
                if prof_name in self.active_profiles:
                    self.active_profiles.remove(prof_name)
                    changed = True
        return changed

class WgTool:
    """
    Class WgTool

        NB Name(s) required - can use 'all' to operate on all names
    """
    # pylint: disable=R0912,R0915
    def __init__(self):

        #
        # Input Configs
        #
        self.conf_dir = 'configs'

        self.conf_serv_dir = f'{self.conf_dir}/server'
        self.conf_serv_file = 'server.conf'

        # do want to add "org" above users?
        self.conf_user_dir = f'{self.conf_dir}/users'
        self.conf_user_confs = None                     # list of file names

        #
        # Output wg configs
        #
        self.wg_dir = 'wg-configs'

        self.wg_serv_dir = f'{self.wg_dir}/server'
        self.wg_serv_conf_file = 'wg0.conf'
        self.wg_users_dir = f'{self.wg_dir}/users'

        self.wg_server = None
        self.wg_users = None

        # data
        self.okay = True
        self.server = None
        self.users = None
        self.opts = WgtOpts(self.conf_dir) # saved options direcory

        if not self.opts.check():
            self.okay = False

        # where & when
        self.now = current_date_time_str()
        self.cwd = os.getcwd()

        if self.opts.init:
            hdr_msg('Init Mode')
            # check for existing server file
            serv_dict = read_server_config(self)
            if serv_dict:
                err_msg('Error: Existing server config found - wont overwrite')
                self.okay = False
            else:
                serv_dict = initial_server_config(self)
                self.server = WgtServer(serv_dict)
                self.server_changed = True
        else:
            #
            # Not init case - read our wg-tool config files
            # Require server config
            #   - user configs may have or create/import or both
            #
            hdr_msg('Normal Mode: using existing setup')
            serv_dict = read_server_config(self)
            user_dicts = read_user_configs(self)

            if not serv_dict:
                err_msg(f'Error: Missing input server config : {self.wg_serv_dir}/{self.wg_serv_conf_file}')
                err_msg('Perhaps you need run "--init" then edit server config template for your setup')
                self.okay = False
                return

            #
            # Server
            #   - convert dictionary to WgtServer attributes
            #   - server holds list of active users.
            # Users
            #   - Each user conf has list of active_profiles
            #   - We keep all users
            #
            # check current active_users
            self.server = WgtServer(serv_dict)
            self.server_changed = False

            self.users_all = []
            self.users_changed = []
            self.users = {}
            if user_dicts:
                for user_dict in user_dicts:
                    user_name = user_dict['name']
                    self.users_all.append(user_name)

                    self.users[user_name] = WgtUser(user_name, user_dict)
                    user = self.users[user_name]

                    # check active profiles are in user config
                    if user.active_profiles:
                        user.refresh_active_profiles()
                        if user.changed:
                            self.user_changed(user_name)
                            self.server_changed = True

            self.refresh_active_users()

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None

    def refresh_active_users(self):
        """
        Remove any active_user which has no real user config
        """
        if not self.server.active_users:
            #warn_msg('Warning: Server has no active_users')
            return

        if not self.users:
            self.server.active_users = None
            return

        active_users = []
        changed = False
        for user_name in self.server.active_users:
            if user_name in self.users :
                active_users.append(user_name)
            else:
                changed = True
        self.server.active_users = active_users
        if changed:
            self.server_changed = True
        return

    def user_exists(self, user_name):
        """ check if user_name exists in users"""
        if self.users:
            return bool(user_name in self.users)
        return False

    def is_user_active(self, user_name):
        """ check if user_name is active """
        if self.server:
            return self.server.is_user_active(user_name)
        return False

    def find_avail_user_ip(self):
        """ get an available IP for new user/config """
        return find_user_ip(self)

    def add_user(self, user_name, prof_name, user_dict) :
        """
        add new user
        """
        user = None
        print(f'Adding {user_name}:{prof_name}')
        if user_name in self.users:
            self.vmsg(f'  {user_name} exists - adding profile')
            user = self.users[user_name]
            prof_dict = user_dict[prof_name]
            user.add_profile(prof_name, prof_dict)
        else:
            self.users[user_name] = WgtUser(user_name, user_dict)
            user = self.users[user_name]
        self.add_active_user_profile(user_name, prof_name)
        if user.changed:
            self.user_changed(user_name)
        return user

    def user_changed(self, user_name):
        """ track any user with changed config """
        if user_name not in self.users_changed:
            self.users_changed.append(user_name)

    def add_active_user(self, user_name):
        """ add user to active_users list """
        if self.user_exists(user_name):
            self.server.add_active_user(user_name)
            self.server_changed = True
        else:
            warn_msg(f'No such user {user_name}. Cannot add to active_users')

    def remove_active_user(self, user_name):
        """
        remove user from active_users
           server returns changed = True/False
        """
        changed = self.server.remove_active_user(user_name)
        if changed:
            self.server_changed = True

    def add_active_user_profile(self, user_name, prof_name):
        """ add prof_name to users active_profile list """
        self.add_active_user(user_name)
        changed = self.users[user_name].add_active_profile(prof_name)
        if changed:
            self.user_changed(user_name)

    def remove_active_user_profile(self, user_name, prof_name):
        """ remove prof_name from users active_profile list """
        self.remove_active_user(user_name)
        changed = self.users[user_name].remove_active_profile(prof_name)
        if changed:
            self.user_changed(user_name)

    def msg(self, txt, end=None):
        """ normal message print """
        print(txt, end=end)

    def vmsg(self, txt, end=None):
        """ verbose message print """
        if self.opts.verb:
            print(txt, end=end)

    def hmsg(self, txt, end=None):
        """ header message print """
        hdr_msg(txt, end=end)

    def emsg(self, txt, end=None):
        """ error message print """
        err_msg(txt, end=end)

    def wmsg(self, txt, end=None):
        """ warn message print """
        warn_msg(txt, end=end)

    def doit(self):
        """
        Run the tool.
          - NB The config writers only write if changed
          - wg config outputs are always updated.
          In general operations are applied to:
            - all users/configs : if 'all' or none specified
            - users/configs specified on command line if any listed
        """
        if self.opts.init :
            write_server_config(self)
            return

        # make any requested user changes
        if self.opts.add_users:
            add_users(self)

        if self.opts.import_user:
            if not import_user(self):
                return
        #
        # Roll keys
        #  - server -> feed new pub key to all users
        #
        if self.opts.upd_user_keys :
            upd_user_keys(self)

        if self.opts.upd_serv_keys:
            upd_serv_keys(self)

        #
        # add_active_user_profile()
        #  - active user or user/configs
        #
        if self.opts.active:
            add_active_users_profiles(self)

        if self.opts.inactive:
            remove_active_users_profiles(self)

        if self.opts.list_users:
            list_users(self)

        # ensure active_users is up to date
        # safety net only - do we need this?
        self.refresh_active_users()

        # save any server config changes
        okay = write_server_config(self)
        if not okay:
            return

        # save any user config changes
        okay = write_user_configs(self)
        if not okay:
            return

        # always update wireguard configs (server and users)
        write_wg_users(self)
        write_wg_server(self)

        # clean up
        cleanup(self)

        hdr_msg('Completed')
