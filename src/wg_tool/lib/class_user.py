# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
  wg-tool base class

    Tool to administer wireguard users and server config with key management
    Driven from 2 types of simple input configs - 1) server.conf and per user.conf
"""
# pylint: disable=invalid-name
from .msg import warn_msg
from .utils import current_date_time_str

class WgtUserProfile:
    """
    Users can have 1 or more Items - each has separate access (phone, laptop etc)
    """
    # pylint: disable=R0902,R0903
    def __init__(self, _prof_name, prof_dict):
        self.Address = None             # str or [str]
        self.PrivateKey = None
        self.PublicKey = None
        self.PresharedKey = None
        self.AllowedIPs = None
        self.Endpoint = None
        self.DnsSearch = False
        self.DnsLinux = False

        self.mod_time = current_date_time_str(fmt='%y%m%d-%H:%M')
        self._changed = None

        self.allowed_ips_own = False    # true if set non-default by user

        for key,val in prof_dict.items():
            setattr(self, key, val)

    def __getattr__(self,name) :
        return None

    def set_changed(self, change_val: bool):
        """ setter for _changed """
        self._changed = change_val

    def get_changed(self):
        """ getter for _changed """
        return self._changed

    def to_dict(self):
        """ return dict of self """
        prof_dict = vars(self)
        return prof_dict

    def refresh_address(self, ipinfo):
        """ ensure have Address for each server net and with right prefixlen """
        (address, changed) = ipinfo.refresh_address(self.Address)
        if changed :
            self.Address = address

        # If not specified in profile use default from ipinfo
        if not self.allowed_ips_own :
            self.AllowedIPs = ipinfo.allowed_ips

        return changed

    def set_allowed_ips_own(self, allowed_ips_def, allowed_ips:str):
        """
        caller sets allowed ips
        """
        changed = False
        if allowed_ips == allowed_ips_def:
            # setting to default -> turn off "own"
            if self.allowed_ips_own:
                self.allowed_ips_own = False
                changed = True
        else:
            # not default
            if not self.allowed_ips_own:
                self.allowed_ips_own = True
                changed = True

        if self.AllowedIPs != allowed_ips:
            self.AllowedIPs = allowed_ips
            changed = True

        if changed:
            self._set_mod_time()
        return changed

    def _set_mod_time(self):
        """ upadate last modify time and mark change"""
        self.mod_time = current_date_time_str(fmt='%y%m%d-%H:%M')
        self._changed = True

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
        self._set_mod_time()
        self._changed = False

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

    def set_changed(self, change_val: bool):
        """ setter for _changed """
        self._changed = change_val

    def get_changed(self):
        """ getter for _changed """
        return self._changed

    def refresh_active_profiles(self):
        """ refresh active_profiles - remove any if profile missing """

        if not self.active_profiles:
            return

        if not self.profile:
            # errr - seems over cautious
            self._set_mod_time()
            self.active_profiles = None
            return

        active_profiles = []
        for prof_name in self.active_profiles:
            if self.profile_exists(prof_name):
                if prof_name not in active_profiles:
                    active_profiles.append(prof_name)
            else:
                self._set_mod_time()

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
                     'mod_time' : self.mod_time,
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
            self._set_mod_time()

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

        if changed:
            self._set_mod_time()
        return changed

    def remove_active_profile(self, prof_name):
        """ remove profile from users active_profile list """
        changed = False
        if self.profile_exists(prof_name):
            if self.active_profiles:
                if prof_name in self.active_profiles:
                    self.active_profiles.remove(prof_name)
                    changed = True
                    self._set_mod_time()
        return changed

    def mod_profile_dns_search(self, dns_search, prof_name):
        """ Set dns search for this profile """
        changed = False
        if self.profile_exists(prof_name):
            profile = self.profile[prof_name]
            if profile.DnsSearch != dns_search:
                profile.DnsSearch = dns_search
                changed = True
        else:
            warn_msg(f'dns_search: {prof_name} not found - ignored')

        if changed:
            self._set_mod_time()
        return changed

    def mod_profile_dns_linux(self, dns_linux, prof_name):
        """ Set dns linux for this profile """
        changed = False
        if self.profile_exists(prof_name):
            profile = self.profile[prof_name]
            if profile.DnsLinux != dns_linux:
                profile.DnsLinux = dns_linux
                changed = True
        else:
            warn_msg(f'dns_linux: {prof_name} not found - ignored')

        if changed:
            self._set_mod_time()
        return changed

    def upd_endpoint(self, wgt, prof_name):
        """
        Ensure current server settings are up to date
        We don't know if profile was internal or not - so user must tell us.
        """
        changed = False
        host_int = wgt.opts.int_serv
        if host_int:
            endpoint = wgt.server.endpoint_int()
        else:
            endpoint = wgt.server.endpoint()

        if self.profile_exists(prof_name):
            profile = self.profile[prof_name]
            if profile.Endpoint != endpoint:
                changed = True
                profile.Endpoint = endpoint
        else:
            warn_msg(f'upd_endpoint: {prof_name} not found - ignored')

        if changed:
            self._set_mod_time()
        return changed

    def mod_profile_address(self, ipinfo, prof_name):
        """
        refresh (server) address to ensure has IP(s) from each server network
        with current prefixlen.
        """
        changed = False
        if self.profile_exists(prof_name):
            profile = self.profile[prof_name]
            if profile.refresh_address(ipinfo):
                changed = True
        else:
            warn_msg(f'mod_profile_address: {prof_name} not found - ignored')

        if changed:
            self._set_mod_time()
        return changed

    def mod_allowed_ips(self, allowed_ips_def:str, allowed_ips:str, prof_name:str):
        """
        Modify the allowed_ips for this user profil
         - string with comma separated list actual cidrs
         - See class_wg where default is set to server provided '0.0.0.0/0, ::/0'
        """
        changed = False
        if not allowed_ips:
            warn_msg(f'mod_allowed_ips: {prof_name} - missing allowed ips')
            return changed

        if self.profile_exists(prof_name):
            profile = self.profile[prof_name]
            changed = profile.set_allowed_ips_own(allowed_ips_def, allowed_ips)
        else:
            warn_msg(f'mod_profile_address: {prof_name} not found - ignored')

        if changed:
            self._set_mod_time()
        return changed

    def _set_mod_time(self):
        """ upadate last modify time """
        self.mod_time = current_date_time_str(fmt='%y%m%d-%H:%M')
        self._changed = True
