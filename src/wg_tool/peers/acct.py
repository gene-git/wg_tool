# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
wg-tool server class
"""
# pylint: disable=invalid-name,too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=duplicate-code
from typing import (Any)
import os

from utils import (Msg, read_toml_file, state_marker)
from utils.debug import pprint
from data import (mod_time_now, get_file_names, write_dict)
from data import (get_vpn_dir)
from net import NetWorks
from config import Opts
from ids import Identity
from ids import Identities

from .profile import Profile


class Acct():
    """
    A "Acct" can be a gateway or a client.

    Characteristics:
    VPN Gateway
     - Host name or ip and listen port information.
     - Will 'acct' with all other accts in this vpn
       (including other gateways)
     - profile name is typically wg0, wg1 etc.

    Client
     - no host info
     - accts with all gateways in the vpn.
       Will have one wiregiard config per profile per gateway
     - acct name is often a user name
     - profile names often reflexct devices (laptop, phone etc)

    db data :
      Data/<vpn>/<acct_name>/
                            Acct.info (name, vpn_name, active, mod_time)
                            <profile-1.conf>
                            <profile-2.conf>
                            ...
    wg data:
      Data-wg/<vpn>/<acct_name>/<profile.conf>
                                ...
    """
    def __init__(self, vpn_name: str, acct_name: str):
        #
        # info
        #
        self.vpn_name: str = vpn_name
        self.name: str = acct_name
        self.active: bool = True
        self.hidden: bool = False
        self.mod_time: str = ''

        #
        # profiles (keyed by profile.name)
        #
        self.profile: dict[str, Profile] = {}

        # internal
        self.changed: bool = False

    def new(self):
        """
        Make this a new acct
        """
        self.changed = True

    def is_active(self) -> bool:
        """
        Returns true if active
        """
        return self.active

    def set_active(self, active: bool):
        """
        Sets active state
        """
        if self.active == active:
            return

        self.active = active
        self.changed = True

    def is_hidden(self) -> bool:
        """
        Returns true if active
        """
        return self.hidden

    def set_hidden(self, hidden: bool):
        """
        Sets hidden state
        """
        if self.hidden == hidden:
            return

        self.hidden = hidden
        if self.hidden:
            self.active = False
        self.changed = True

    def rename_acct(self, acct_name_new: str) -> bool:
        """
        Rename this acct to acct_new
        NB we do not change any directory names.
            Caller is responsible (vpn)
        """
        if not acct_name_new:
            Msg.err('Acct rename {self.name}: no name provided\n')
            return False

        if acct_name_new == self.name:
            Msg.warn(f'Acct rename has same name {acct_name_new}\n')
            return True

        # change my name
        self.name = acct_name_new
        self.changed = True
        for prof in list(self.profile.values()):
            prof.ident.acct_name = acct_name_new
        self.refresh_ids()
        return True

    def rename_prof(self, prof_name: str, prof_name_new: str) -> bool:
        """
        Rename one profile.
        """
        if not (prof_name and prof_name_new):
            Msg.err('Prof rename - missing name\n')
            Msg.plain(f' {self.name}: {prof_name} -> {prof_name_new}\n')
            return False

        prof = self.profile.get(prof_name)
        if not prof:
            Msg.err(f'Prof rename {self.name} no such prof {prof_name}l\n')
            return False

        if not prof.rename_prof(prof_name_new):
            return False
        return True

    def rename_vpn(self, vpn_name: str) -> bool:
        """
        Update vpn name
        Returns True if all well
        """
        if self.vpn_name != vpn_name:
            self.vpn_name = vpn_name
            self.changed = True
            for prof in list(self.profile.values()):
                if not prof.rename_vpn(vpn_name):
                    return False
        return True

    def write(self, opts: Opts) -> bool:
        """
        Write self out with profile data in separate files.
        todo: add check that info is valid
        Returns True if all good.
        """
        # if not self.changed:
        #     return True

        work_dir = opts.work_dir

        vpn_name = self.vpn_name
        acct_name = self.name
        Msg.plainverb(f'  Acct {acct_name}\n', level=3)

        vpn_dir = get_vpn_dir(work_dir, vpn_name)
        acct_dir = os.path.join(vpn_dir, acct_name)

        #
        # Acct Info File
        #
        if not self.write_info(acct_dir):
            return False

        #
        # profile data
        #
        for (_prof_name, prof) in self.profile.items():
            if not prof.write(opts, acct_dir):
                return False
        return True

    def read(self, work_dir: str) -> bool:
        """
        Read acct file and profile files.
        Returns True if all good.

        Acct keeps its data in:

            vpn_dir/acct_name/
                 acct_name.info
                 prof-1
                 prof-2
                 ...
        """
        vpn_name = self.vpn_name
        acct_name = self.name

        vpn_dir = get_vpn_dir(work_dir, vpn_name)
        acct_dir = os.path.join(vpn_dir, acct_name)

        #
        # acct info file
        #
        self.read_info(acct_dir)

        #
        # profiles - <prof-name>.prof
        # Must be only files with .prof extension.
        #
        prof_ext = '.prof'
        prof_files = get_file_names(acct_dir, prof_ext)
        if prof_files:
            for filename in prof_files:
                prof_path = os.path.join(acct_dir, filename)
                prof = Profile()
                if not prof.read(prof_path):
                    return False

                ident = prof.ident
                self.profile[ident.prof_name] = prof

                # Make sure profile has acct_name
                if ident.acct_name != acct_name:
                    ident.acct_name = acct_name
                    prof.changed = True

        return True

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize
        """
        attrib: dict[str, Any] = {}
        for (k, v) in vars(self).items():
            if k == 'profile':
                profile: dict[str, Any] = {}
                attrib[k] = profile
                for (name, prof) in self.profile.items():
                    profile[name] = prof.to_dict()
            else:
                attrib[k] = v
        return attrib

    def to_dict_no_profile(self) -> dict[str, Any]:
        """
        Serialize self but skip 'profile' and 'changed'.
        """
        attrib: dict[str, Any] = {}
        for (k, v) in vars(self).items():
            if k not in ('profile', 'changed'):
                attrib[k] = v
        return attrib

    def from_dict_no_profile(self, data_dict: dict[str, Any]):
        """
        Import from dictionary.
        """
        if not data_dict:
            return

        for (k, v) in data_dict.items():
            if k != 'profile':
                setattr(self, k, v)

    def from_dict(self, data_dict: dict[str, Any]):
        """
        Import from dictionary.
        """
        for (k, v) in data_dict.items():
            if k == 'profile':
                # load profiles
                for (name, prof_dict) in v.items():
                    prof = Profile()
                    prof.from_dict(prof_dict)
                    self.profile[name] = prof
            else:
                setattr(self, k, v)

    def active_profile_names(self) -> tuple[list[str], list[str]]:
        """
        Return list of active profile names

        Returns:
            (gw_names_list, cl_names_list)
        """
        gw_names: list[str] = []
        cl_names: list[str] = []
        if not self.active:
            return (gw_names, cl_names)

        for (name, prof) in self.profile.items():
            if not prof.active:
                continue
            if prof.is_gateway():
                gw_names.append(name)
            else:
                cl_names.append(name)
        return (gw_names, cl_names)

    def active_profile_id_str(self) -> tuple[list[str], list[str]]:
        """
        Return list of active profile ident.id_str

        Returns:
            (gw_id_str, cl_id_str)
        """
        gw_id_str: list[str] = []
        cl_id_str: list[str] = []
        if not self.active:
            return (gw_id_str, cl_id_str)

        for (_prof_name, prof) in self.profile.items():
            if not prof.active:
                continue

            if prof.is_gateway():
                gw_id_str.append(prof.ident.id_str)
            else:
                cl_id_str.append(prof.ident.id_str)
        return (gw_id_str, cl_id_str)

    def add_prof(self, prof_name: str, address: list[str]) -> Profile | None:
        """
        Make a new server

         - address must exist - caller should generate or
           validate input address is unused and in the right network.

        Note that alternate internal view(s) (host:port) are taken from:
           host.host_alt / host.port_alt

        Args:
            prof_name (str):
                Profile name. Can be empty of only creating acct
        """
        if not prof_name:
            return None

        if prof_name and prof_name in self.profile:
            Msg.err(f'{prof_name} already exists\n')
            return None

        self.mod_time = mod_time_now()

        prof = Profile()
        ident = prof.ident

        ident.prof_name = prof_name
        ident.vpn_name = self.vpn_name
        ident.acct_name = self.name
        ident.new_tag()
        ident.refresh()

        prof.new_key_pair()
        prof.Address = address
        prof.changed = True
        self.changed = True
        self.profile[prof_name] = prof

        return prof

    def read_info(self, acct_dir: str):
        """
        Load the info file.
        - info: name, active, mod_time
        - NB: name taken from directory name
        """
        info_file = os.path.join(acct_dir, 'Acct.info')

        if os.path.isfile(info_file):
            info_dict = read_toml_file(info_file)
            for (k, v) in info_dict.items():
                setattr(self, k, v)
        else:
            Msg.warn(f'Warning: missing info file: {info_file}\n')
            Msg.plain('  repairing.\n')

            self.name = os.path.basename(acct_dir)
            self.vpn_name = os.path.basename(os.path.dirname(acct_dir))
            self.active = True
            self.hidden = False
            self.mod_time = mod_time_now()
            self.changed = True

    def write_info(self, acct_dir: str) -> bool:
        """
        Write the info file.
        - info: name, active, mod_time
        - NB: name taken from directory name
        """
        info_file = os.path.join(acct_dir, 'Acct.info')

        data_dict = self.to_dict_no_profile()

        title = f'Acct.info: {self.name}'
        (ok, _changed) = write_dict(title, data_dict, info_file)
        if not ok:
            return False
        return True

    def show_list(self, opts: Opts):
        """
        List acct and profiles
        <name> (active) <mod-date> : <prof-1>
        """
        state = state_marker(self.hidden, self.active)

        if not opts.brief:
            Msg.info(f'\n{"":4s}{state} {self.name:<12s} {self.mod_time}:\n')

        if not self.profile:
            return

        # all profiles unless specified
        vpn_name = self.vpn_name
        acct_name = self.name
        ids = opts.idents

        profs: list[Profile] = []
        prof_names = ids.prof_names(vpn_name, acct_name)
        if len(prof_names) > 0:
            prof_names = sorted(prof_names)
            for name in prof_names:
                prof = self.profile.get(name)
                if prof:
                    profs.append(prof)
                else:
                    Msg.warn(f'No such profile {name}\n')
        else:
            # all profiles
            psorted = dict(sorted(self.profile.items()))
            profs = list(psorted.values())

        # show them
        # first: bool = True
        for prof in profs:
            # if not first:
            #     Msg.plain('\n')
            prof.show_list(opts)
            # if first:
            #     first = False

    def prof_from_pubkey(self, pubkey_str) -> Profile | None:
        """
        Locate profile with matching pubkey_str
        """
        for prof in list(self.profile.values()):
            if prof.PublicKey == pubkey_str:
                return prof

        # no match
        return None

    def refresh_dns_servers(self, dns_list: list[str]):
        """
        Rerfesh dns server list
        """
        for prof in list(self.profile.values()):
            prof.refresh_dns_servers(dns_list)
            if prof.changed:
                self.changed = True

    def refresh_address_wg(self, networks: NetWorks) -> bool:
        """
        Rerfesh profile AddressWg
        Args:
            vpn_name (str):
                This vpn name

            networks (NetWorks):
                List of networks for this vpn
        """
        for prof in list(self.profile.values()):
            if not prof.refresh_address_wg(networks):
                Msg.err('Error updating acct {self.name}\n')
                return False
            if prof.changed:
                self.changed = True
        return True

    def refresh_is_gateway(self):
        """
        Refresh whether profile is a gateway
        """
        for prof in list(self.profile.values()):
            prof.refresh_is_gateway()

    def refresh_privkey(self):
        """
        Refresh any missing keys
        """
        for prof in list(self.profile.values()):
            prof.refresh_privkey()

    def refresh_ids(self):
        """
        Refresh profile id
        """
        for prof in list(self.profile.values()):
            if prof.refresh_id():
                self.changed = True

    def refresh_nets(self):
        """
        Refresh any profile nets_shared
        Checks intenet wanted/offered against
        nets_shared_wanted/nets_shared
        """
        for prof in list(self.profile.values()):
            prof.refresh_nets()

    def new_key_pairs(self, idents: Identities) -> bool:
        """
        Generate new keys for ids
        """
        prof_names: list[str] = []
        vpn_name = self.vpn_name
        acct_name = self.name

        for ident in idents.ids:
            if ident.vpn_name == vpn_name and ident.acct_name == acct_name:
                if ident.prof_name in self.profile:
                    prof_names.append(ident.prof_name)
                else:
                    Msg.err(f'Unknown profile: {ident.id_str}\n')
                    return False

        if not prof_names:
            # nothing to do
            return True

        #
        # Ok do it
        #
        for prof_name in prof_names:
            prof = self.profile[prof_name]
            if not prof.new_key_pair():
                return False
        self.changed = True
        return True

    def find_prof(self, prof_name) -> Profile | None:
        """
        Find prof if have it.
        """
        if prof_name in self.profile:
            return self.profile[prof_name]
        return None

    def acct_exists(self, ident: Identity) -> bool:
        """
        Check if profile exists.
        """
        if ident.prof_name in self.profile:
            return True
        return False

    def tag_to_ident(self, tag: str) -> Identity | None:
        """
        Return the profile id associated with tag.
        or None if not found
        """
        if not tag:
            return None

        ident: Identity | None = None
        for prof in list(self.profile.values()):
            ident = prof.tag_to_ident(tag)
            if ident:
                return ident
        return None

    def tag_to_prof(self, tag: str) -> Profile | None:
        """
        Return the profile associated with tag.
        or None if not found
        """
        if not tag:
            return None

        for prof in list(self.profile.values()):
            if prof.ident.tag == tag:
                return prof
        return None

    def tag_id_map(self) -> dict[str, str]:
        """
        Generate a dictionary of tag -> profile id string mappings
        """
        tag_id_all: dict[str, str] = {}
        for prof in list(self.profile.values()):
            tag_id = prof.tag_id_map()
            if tag_id:
                tag_id_all |= tag_id
        return tag_id_all

    def gateway_ids(self) -> list[str]:
        """
        Get list of id_strings of any gateway profiles
        """
        gw_names: list[str] = []
        for prof in list(self.profile.values()):
            if prof.is_gateway():
                gw_names.append(prof.ident.id_str)
        return gw_names

    def has_any_profiles(self) -> bool:
        """
        Returns true if account has 1 or more profiles
        """
        if len(self.profile) > 0:
            return True
        return False

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)
