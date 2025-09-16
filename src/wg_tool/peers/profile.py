# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Profile
"""
# pylint: disable=invalid-name, too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=duplicate-code
from typing import (Any, Self)
import os
from copy import deepcopy

from utils import Msg
from utils import read_toml_file
from utils import dict_to_toml_string

from config import Opts

from crypto import gen_key_pair
from data import (write_dict, mod_time_now)
from net import NetWorks
from net import internet_networks
from ids import Identity

from .profile_base import ProfileBase
from .wg_address import set_wireguard_address
from .show_list import show_list


class Profile(ProfileBase):
    """
    Profile is the basic unit of a wireguard peer.

    A peer is denoted by it's ID: vpn.account.profile names.
    """
    def is_gateway(self):
        """
        Returns true if a gateway
        Gateway has endpoint. It may or may not have nets_offered
        it shares.
        Some clients may share internal_networks - "client_gateways".
        They are not gateways but once they connect, they
        offer access to some networks (typically LAN).
        """
        if self.Endpoint:
            return True
        return False

    def refresh_is_gateway(self):
        """
        Refresh the is_gw flag
        Returns True if changed.
        """
        is_gw = self.is_gateway()
        if self.is_gw != is_gw:
            self.is_gw = is_gw

    def is_active(self) -> bool:
        """
        Return true if active
        """
        return self.active

    def set_active(self, is_active: bool):
        """
        Set active state
        """
        if self.active == is_active:
            return

        self.active = is_active
        self.changed = True

    def is_hidden(self) -> bool:
        """
        Return true if hidden
        """
        return self.hidden

    def set_hidden(self, hidden: bool):
        """
        Set hidden state
        """
        if self.hidden == hidden:
            return

        self.hidden = hidden
        if self.hidden:
            self.active = False
        self.changed = True

    def new_key_pair(self) -> bool:
        """
        Generate new key set and replace old keys
        with these new ones.
        """
        (key_prv, key_pub) = gen_key_pair()
        self.PrivateKey = key_prv
        self.PublicKey = key_pub
        self.changed = True
        # new key can have psks - not legacy any more.
        self.no_psk_tags = []
        return True

    def read(self, fpath: str) -> bool:
        """
        Read the profile file "fpath"
        """
        if not fpath:
            return True
        file = os.path.basename(fpath)
        prof_name_file = file.removesuffix('.prof')
        prof_dict = read_toml_file(fpath)

        # consistency check
        id_dict = prof_dict.get('ident')
        if id_dict:
            prof_name = id_dict.get('prof_name')
            if prof_name != prof_name_file:
                txt = f'{prof_name} vs {prof_name_file}'
                Msg.err(f'Error: profile name mismatch: {txt}\n')
                return False
        else:
            Msg.warn('Error - missing id from {fpath}\n')

        # save attribs
        self.from_dict(prof_dict)
        return True

    def file_path(self, acct_dir: str) -> str:
        """
        Returns profile file path
        """
        fpath: str = ''
        if not acct_dir:
            return fpath

        name = self.ident.prof_name
        fpath = os.path.join(acct_dir, name + '.prof')
        return fpath

    def remove_file(self, acct_dir: str) -> bool:
        """
        Delete the profile file.
        """
        fpath = self.file_path(acct_dir)
        if not fpath or not os.path.exists(fpath):
            Msg.warn(f'Unable to remove profile file {fpath}\n')
            return False
        try:
            os.unlink(fpath)
        except OSError as exc:
            Msg.err(f'Error removing file {fpath} {exc}\n')
            return False
        return True

    def write(self, opts: Opts, acct_dir: str) -> bool:
        """
        Write file "fpath"
        todo: add date-dir + link
        """
        if not acct_dir:
            return True

        if self.internet_offered and self.internet_wanted:
            self.internet_wanted = False
            self.changed = True

        # name = self.ident.prof_name
        id_str = self.ident.id_str

        fpath = self.file_path(acct_dir)
        prof_dict = self.to_dict()

        # write them
        prof_name = self.ident.prof_name
        acct_name = self.ident.acct_name
        vpn_name = self.ident.prof_name

        title = f'{vpn_name} {acct_name} {prof_name}'

        (ok, changed) = write_dict(title, prof_dict, fpath)
        if not ok:
            return False

        if changed and not opts.brief:
            Msg.plain(f'    {id_str} updated\n')
        return True

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        Skip: 'changed'
        """
        # attribs: dict[str, Any] = vars(self).copy()
        attribs: dict[str, Any] = deepcopy(vars(self))
        attribs = self.attribs_drop(attribs)

        adict: dict[str, Any] = {}
        for (k, v) in attribs.items():
            if isinstance(v, Identity):
                adict[k] = v.to_dict()
            else:
                adict[k] = v
        return adict

    def from_dict(self, attribs: dict[str, Any]):
        """
        Install attribs from dictionarey.
        """
        # remove any no longer used
        attribs = self.attribs_drop(attribs)

        for (k, v) in attribs.items():
            if k == 'ident':
                ident = Identity()
                ident.from_dict(v)
                self.ident = ident
            else:
                setattr(self, k, v)

    def merge_from_dict(self, attribs: dict[str, Any]):
        """
        Merge attribs from dictionarey.
        """
        drops = ('Address', 'AddressWg', 'PrivateKey', 'PublicKey',
                 'pre_up', 'pre_down', 'ident',
                 'is_gw', 'mod_time', 'changed', 'AllowedIPs')

        attribs = self.attribs_drop(attribs, drops=drops)

        for (k, v) in attribs.items():
            current = getattr(self, k)
            if _is_different(current, v):
                # if (v or isinstance(v, bool)) and v != current:
                setattr(self, k, v)
                Msg.plain(f'  {k}\n')
                self.changed = True
        if not self.changed:
            Msg.plain('  Profile unchanged\n')

    def copy(self, prof_from: Self) -> bool:
        """
        Copy from 'prof_from'.
        when they are taken from "prof_from".
        psk pairs to use the same psk as the prof_from it came from.

        Some fields are never copied:
            name, acct_name, vpn_name, id_hash
            Address, AddressWg
        """
        from_dict = prof_from.to_dict()
        #
        # remove things we do not want copied.
        #
        drops: tuple[str, ...]
        drops = ('ident', 'changed', 'mod_time', 'Address', 'AddressWg')

        from_dict = self.attribs_drop(from_dict, drops=drops)

        #
        # copy the rest
        #
        self.from_dict(from_dict)
        self.changed = True
        self.mod_time = mod_time_now()
        return True

    def merge(self, data: dict[str, Any]) -> bool:
        """
        Merga the data.
        Caller has used the tag in dictionary to locate this
        profile usin vpns:tag:to_vpn_prof()
        """
        if not data:
            return True

        Msg.info(f'Merging edits for {self.ident.id_str}\n')

        # double check the tag is correct
        ident_in = data.get('ident')
        if not ident_in:
            Msg.err('Merge data missing tag\n')
            return False

        tag = ident_in.get('tag')
        if not tag or tag != self.ident.tag:
            Msg.err(f'Merge data tag mismatch: {tag} vs {self.ident.tag}\n')
            return False

        endpoint = data.get('Endpoint')
        if endpoint:
            # check has host:port
            (addr, _delim, port) = endpoint.rpartition(':')
            if not (addr and port):
                Msg.err(f'Bad Endpoint: {endpoint}\n')
                Msg.plain('  Needs to be host:port\n')
                return False

        #
        # sanity checks
        #
        if data.get('internet_offered') is True:
            data['internet_wanted'] = False

        if data.get('internet_wanted') is True:
            data['internet_offered'] = False

        #
        # Do the actual merge
        #
        self.merge_from_dict(data)

        if self.changed:
            self.mod_time = mod_time_now()

        return True

    def attribs_drop(self, attribs: dict[str, Any],
                     drops: tuple[str, ...] = ()) -> dict[str, Any]:
        """
        Return dictionary with drop keys removed
        These attributes are not saved.
        Always generated internally.
        """
        drops += ('changed', 'is_gw', 'mod_time', 'peer_id')
        drops = tuple(set(drops))

        attribs_keep: dict[str, Any] = {}
        for (key, value) in attribs.items():
            if key in drops or value is None:
                continue
            attribs_keep[key] = value
        return attribs_keep

    def attribs_keep(self, attribs: dict[str, Any],
                     keeps: tuple[str, ...] = ()) -> dict[str, Any]:
        """
        Return dictionary with only keep keys
        Remainder are ignored.
        """
        keeps = tuple(set(keeps))

        attribs_keep: dict[str, Any] = {}
        for key in keeps:
            value = attribs.get(key)
            if value:
                attribs_keep[key] = value
        return attribs_keep

    def refresh_gateway_accts(self, acct_name: str, ipinfo):
        """
        When new gateways added - need to refresh
        the them for each client and other gateways.
        """

    def refresh_keepalive(self, keepalive: int):
        '''
        Update keepalive if needed
        '''
        if keepalive != self.PersistentKeepalive:
            self.PersistentKeepalive = keepalive
            self.changed = True

    def refresh_nets(self) -> bool:
        """
        Check that "any" ips destined for internet are not included
        in nets_offered/wanted.
        If they are then set internet_offered instead

        """
        if not (self.nets_wanted or self.nets_offered):
            return True

        #
        # nets wanted
        #
        (has_internet, nets_clean) = _nets_drop_internet(self.nets_wanted)
        if has_internet:
            self.internet_wanted = True
            self.nets_wanted = list(set(nets_clean))
            self.changed = True

        #
        # nets offered
        #
        (has_internet, nets_clean) = _nets_drop_internet(self.nets_offered)
        if has_internet:
            self.internet_offered = True
            self.nets_offered = list(set(nets_clean))
            self.changed = True

        return True

    def _set_mod_time(self):
        """ upadate last modify time and mark change"""
        self.mod_time = mod_time_now()
        self.changed = True

    def read_file(self, fpath: str) -> bool:
        """
        Load data from file
        """
        data_dict = read_toml_file(fpath)
        if not data_dict:
            return False
        self.from_dict(data_dict)
        return True

    def show_list(self, opts: Opts):
        """
        Display profile on one line with no newline.
        vpn caller does line breaks
        """
        show_list(self, opts)

    def refresh_dns_servers(self, dns_list: list[str]):
        """
        Refresh current dns servers
        """
        if self.dns != dns_list:
            self.dns = dns_list
            self.changed = True

    def refresh_address_wg(self, networks: NetWorks) -> bool:
        """
        Make sure AddressWg is up to date.
        Wireguard address is IP address but the cidr prefix set to prefixlen of
        network. i.e. cidr but with host bits set to the address.
        """
        if not set_wireguard_address(networks, self):
            Msg.err(f'Error setting wireguard address(es): {self.Address}')
            return False
        return True

    def refresh_privkey(self):
        """
        Add missing private key
        """
        if not self.PrivateKey:
            name = self.ident.prof_name
            acct_name = self.ident.acct_name
            Msg.info(f' Key refresh: {acct_name}:{name}\n')
            self.new_key_pair()

    def refresh_id(self) -> bool:
        """
        Internal so no change mark
        Returns true if changed
        """
        if self.ident.refresh():
            self.changed = True
        return self.changed

    def for_edit(self) -> str:
        """
        Return printable profile string.

        Note - exclude any keys.
        """
        pstr = _profile_str_for_edit(self)
        return pstr

    def rename_prof(self, new_name: str) -> bool:
        """
        Rename self.
        Returns True if all wel..
        """
        if self.ident.set_prof_name(new_name):
            self.changed = True
        return True

    def rename_acct(self, new_name: str) -> bool:
        """
        Rename acct.
        Returns True if all wel..
        """
        if self.ident.set_acct_name(new_name):
            self.changed = True
        return True

    def rename_vpn(self, new_name: str) -> bool:
        """
        Rename vpn
        """
        if self.ident.set_vpn_name(new_name):
            self.changed = True
        return True

    def id_string(self) -> str:
        """
        Return id = vpn_name:acct_name:prof_name
        """
        ident = self.ident
        ident.refresh()
        id_str = ident.id_str
        return id_str

    def tag_to_ident(self, tag: str) -> Identity | None:
        """
        Return identity with natching tag.
        Else return None
        """
        if not tag:
            return None
        if self.ident.tag == tag:
            return self.ident
        return None

    def tag_id_map(self) -> dict[str, str]:
        """
        Generate a dictionary of tag -> profile id string mappings
        """
        ident = self.ident

        tag_map: dict[str, str] = {}
        name = ident.acct_name + ':' + ident.prof_name
        tag_map[ident.tag] = name
        return tag_map


def _profile_str_for_edit(prof: Profile) -> str:
    """
    Generate editable profile string.

    can be existing or new.

    Some fields are never written:
        Address AddressWg
        PrivateKey PublicKey PresharedKey
        dns_postup dns_postdn
    """
    #
    # Drop things we dont want to put in edit file
    # For now skip: pre up / down
    #
    prof_dict = prof.to_dict()
    drops = ('Address', 'AddressWg', 'PrivateKey', 'PublicKey',
             'pre_up', 'pre_down', 'AllowedIPs',
             'is_gw', 'mod_time', 'changed', 'no_psk_tags',
             'dns_postup', 'dns_postdn')

    #
    # ident:
    #   - only keep tag for the edit file
    #     nothing else is needed or editable.
    #
    prof_dict['ident'] = {'tag': prof_dict['ident']['tag']}

    edit_dict: dict[str, Any] = {}
    for (k, v) in prof_dict.items():
        if k in drops:
            continue
        edit_dict[k] = v

    pstr = ''
    pstr += '# Note 1: Only gateways have endpoints\n'
    pstr += '# Note 2: post up and down (for linux peers)\n'
    pstr += '#\n\n'

    if not edit_dict.get('post_up'):
        post_up = ['/usr/bin/nft -f /etc/wireguard/scripts/postup.nft']
        pstr += f'# post_up = {post_up}\n'

    if not edit_dict.get('post_down'):
        post_down = ['/usr/bin/nft flush ruleset']
        pstr += f'# post_down = {post_down}\n'
    pstr += '\n'
    pstr += dict_to_toml_string(edit_dict, drop_empty=False)

    return pstr


def _is_different(old: Any, new: Any) -> bool:
    """
    Return True if new is different than current
    handles simple numbers, str, bool and list.
    """
    if new is None:
        return False

    if isinstance(old, list):
        if not isinstance(new, list):
            Msg.err(f'Expecting a list not : {new} (ignored)\n')
            return False

        return bool(set(old) != set(new))

    if new != old:
        return True
    return False


def _nets_drop_internet(nets: list[str]) -> tuple[bool, list[str]]:
    """
    Remove internet IPs from list aand return True if so
    along with list with them removed
    """
    internets = internet_networks()
    nets_clean: list[str] = []
    found_internet: bool = False
    for net in nets:
        if net in internets:
            found_internet = True
        else:
            nets_clean.append(net)
    return (found_internet, nets_clean)
