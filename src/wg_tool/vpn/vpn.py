# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Gateways
"""
# pylint: disable=too-many-public-methods

from utils import (Msg, state_marker)
from utils.debug import pprint

from config import Opts

from data import (get_acct_names)
from data import rename_acct_dir
from data import unlink_profile

from peers import Acct
from peers import WgConfig
from peers import Profile

from rpt import PeerReport
from rpt import AcctProfile

from ids import Identity
from ids import Identities

from net import NetsShared

from vpninfo import VpnInfo


class Vpn():
    """
    One VPN: vpn network info & List of accts.

    Peers are all gateways and clients associated with
    this vpn.
    todo: Check that all accts IPs are from vpn network.
          for each profile check Address is in any
          of the networks in vpninfo.
    """
    def __init__(self, opts: Opts, vpn_name: str):
        # Opts shared from top level via Vpns to us
        self.okay: bool = True
        self.opts: Opts = opts
        self.name: str = vpn_name
        self.vpninfo: VpnInfo = VpnInfo(opts.work_dir, vpn_name)
        self.accts: dict[str, Acct] = {}

        self.nets_shared: NetsShared = NetsShared()

    def is_active(self) -> bool:
        """
        Returns true of this vpn is active
        """
        return self.vpninfo.is_active()

    def set_active(self, is_active: bool):
        """
        Mark vpn (in)active
        """
        self.vpninfo.set_active(is_active)

    def is_hidden(self) -> bool:
        """
        Returns true of this vpn is hidden
        """
        return self.vpninfo.is_hidden()

    def set_hidden(self, hidden: bool):
        """
        Mark vpn hidden (or not)
        """
        self.vpninfo.set_hidden(hidden)

    def read(self):
        """
        Read Vpn.info and any accts data
        """
        self.vpninfo = VpnInfo(self.opts.work_dir, self.name)
        self.read_accts()
        self.refresh()

    def refresh(self) -> bool:
        """
        Refresh dns_postupdn
        Refresh wiregued addresses
        """
        #
        # dns refresh:
        # - check/update vpninfo.dns_gateways (dns from every gateway)
        # - check/update client accts using dns_linux with current
        #   vpninfo.dns / vpninfo.dns_gateways (ditto for dns search)
        # - ensure profile have up to date AddressWG
        # - refresh dns server list
        #
        vpninfo = self.vpninfo
        acct_list = list(self.accts.values())

        #
        # dns from gateways
        #
        dns_gateways: list[str] = []
        dns_search_gateways: list[str] = []
        for acct in acct_list:
            (gw_names, _cl_names) = acct.active_profile_names()
            for name in gw_names:
                prof = acct.profile[name]
                if prof.dns:
                    dns_gateways += prof.dns
                if prof.dns_search:
                    dns_search_gateways += prof.dns_search
        #
        # update vpn dns/dns_search if different
        # and get current dns_postup/dn - this ignores any profile
        # dns/dns_search - lets add a flag to client profiles
        # to use dns from vpn: use_vpn_dns
        # If false the use own dns
        # dns is now gateways or clients with use_vpn_dns = False
        # gateways ignore use_vpn_dns
        # We sh
        if dns_gateways or dns_search_gateways:
            vpninfo.put_dns_gateway(dns_gateways, dns_search_gateways)

        #
        # Make sure AddressWg is up to date
        #
        if self.vpninfo:
            networks = self.vpninfo.networks
            for acct in list(self.accts.values()):
                if not acct.refresh_address_wg(networks):
                    self.okay = False
                    Msg.err(f'Error: {self.name}\n')

        #
        # Refresh is_gateway flag
        #
        for acct in acct_list:
            acct.refresh_is_gateway()

        #
        # Check for valid private key
        #
        for acct in acct_list:
            acct.refresh_privkey()

        #
        # Refresh profile ids
        #
        for acct in acct_list:
            acct.refresh_ids()

        #
        # refresh psks
        # every pair with 1 or more gateways
        # has a PSK they share.
        #
        self.refresh_psks()

        #
        # Refresh nets_shared
        #
        self.refresh_nets()

        return True

    def refresh_nets(self):
        """
        Update shared network info
        nets_shared are for newtork(s) a peer shares with other
        peers. This excludes "internet" any IPs
        """
        #
        # remove any "internet" from nets_shared/_wanted
        # replace with internet_offered/_wanted
        #
        for (_name, acct) in self.accts.items():
            acct.refresh_nets()

        #
        # Update NetsShared
        #
        nets_shared = self.nets_shared

        for (_name, acct) in self.accts.items():
            if not acct.active:
                continue

            for (_pname, prof) in acct.profile.items():
                if not prof.active:
                    continue

                id_str = prof.ident.id_str

                if prof.nets_wanted:
                    cidrs = prof.nets_wanted.copy()
                    nets_shared.add_wanted_by(id_str, cidrs)

                if prof.nets_offered:
                    cidrs = prof.nets_offered.copy()
                    nets_shared.add_offered_by(id_str, cidrs)

    def new_key_pairs(self, idents: Identities) -> bool:
        """
        Gnereate new keys
        """
        vpn_idents: Identities = Identities()
        for ident in idents.ids:
            # filter to our own vpn.accts
            if ident.vpn_name == self.name:
                if ident.acct_name in self.accts:
                    vpn_idents.ids.append(ident)
                else:
                    Msg.err(f'Unknown account {ident.id_str}\n')
                    return False

        if not vpn_idents.ids:
            # no matches
            return True

        #
        # Now separate by account name so
        # can pass all acct.profiles to acct.
        # acct can then check if all profiles are valid
        # before making any changes
        #
        acct_idents: dict[str, Identities] = {}
        for ident in vpn_idents.ids:
            acct_name = ident.acct_name
            if not acct_idents[acct_name]:
                acct_idents[acct_name] = Identities()

            acct_idents[acct_name].ids.append(ident)

        #
        # ask each acct to make new keys
        #
        for (acct_name, these) in acct_idents.items():
            acct = self.accts[acct_name]
            if not acct.new_key_pairs(these):
                return False

        return True

    def refresh_psks(self):
        """
        Refresh the psk each pair of peers with at least
        one gateway uses.

        While we loop on tags (A, B) as well as (B,A)
        Psks handles this by using sorted tag pairs.

        So we loop on gateways paired with
        all other peers.

        NB Some legacy clients may not have had PSK.
        To ensure they dont break by adding one, such
        clients mark the one server they dont share one with.

        # should we skip dead profiles here?
        """
        # list of (tag, list[tags not to psk with]) tuples
        gw_tag_infos = self._get_tag_infos(gw_only=True)
        tag_infos = self._get_tag_infos()

        #
        # Pass 1: get/generate all psk pairs
        #
        psks = self.vpninfo.psks
        for gw_tag_info in gw_tag_infos:
            gw_tag = gw_tag_info[0]

            for peer_tag_info in tag_infos:
                peer_tag = peer_tag_info[0]
                no_psk_tags = peer_tag_info[1]

                # skip self
                if peer_tag == gw_tag:
                    continue

                # check if pair is a legacy with no psk pair.
                no_psk = False
                if gw_tag in no_psk_tags:
                    no_psk = True

                psks.get_set_shared_key(gw_tag, peer_tag, no_psk=no_psk)

        #
        # Pass 2
        # - delete any tags which no longer are valid tags.
        # - could happen if user manually removes a profile file
        #   from Data/<vpn>/<acct>/<prof>
        #
        if tag_infos:
            known_tags = [info[0] for info in tag_infos]
            known_gw_tags = [info[0] for info in tag_infos]
            psks.clean_unknown_tags(known_gw_tags, known_tags)

    def _get_tag_infos(self, gw_only: bool = False
                       ) -> list[tuple[str, list[str]]]:
        """
        Return list of tags of every peer.
        if gw_only is True, then only gateway peers are returned.

        Returns:
            list[tuple[tag, list[tags_no_psk]]]

            where tags_no_psk lists tags of other peers this has no psk with.
            Some legacy peers had no PSK,
        """
        tags: list[tuple[str, list[str]]] = []
        for (_acct_name, acct) in self.accts.items():
            for (_prof_name, prof) in acct.profile.items():
                if gw_only and not prof.is_gw:
                    continue
                tag = prof.ident.tag
                no_psk_tags = prof.no_psk_tags
                tags.append((tag, no_psk_tags))
        return tags

    def write(self):
        """
        Read Vpn.info and any peer data
        """
        if not self.opts.brief:
            Msg.info(f'  Checking {self.name}\n')
        self.refresh()

        # get tag -> id mapping
        tag_map: dict[str, str] = self.tag_id_map()
        if not self.vpninfo.write_file(self.opts.work_dir, tag_map):
            self.okay = False
            return
        self.write_accts()

    def add_acct(self, acct_name: str) -> Acct | None:
        """
        Add a acct
         - what about profile?
        """
        if acct_name and acct_name in self.accts:
            Msg.err(f'{acct_name} already exists\n')
            return None

        vpn_name = self.name
        acct = Acct(vpn_name, acct_name)
        acct.changed = True
        self.accts[acct_name] = acct
        return acct

    def add_acct_prof(self, acct_name: str, prof_name: str) -> Profile | None:
        """
        Make a new prof (acct may exist)
        """
        new_id = f'{self.name}:{acct_name}:{prof_name}'
        Msg.info(f'Adding new {new_id}\n')

        if not (acct_name and prof_name):
            Msg.err('Error incomplete id\n')
            return None
        #
        # Acct
        #
        acct: Acct | None
        if acct_name in self.accts:
            acct = self.accts[acct_name]
        else:
            acct = self.add_acct(acct_name)
            if not acct:
                return None
        #
        # Profile
        #
        prof = acct.find_prof(prof_name)
        if prof:
            Msg.err(f'profile {acct_name}:{prof_name} already exists\n')
            return None

        txt = 'If adding a gateway profile, you *must* edit it'
        txt += '  and add an Endpoint'
        Msg.warnverb('txt\n', level=2)

        vpninfo = self.vpninfo
        new_ips = vpninfo.find_new_address()
        prof = acct.add_prof(prof_name, new_ips)
        return prof

    def read_accts(self) -> bool:
        """
        Load any existing acct data
        """
        if not self.opts.brief:
            Msg.hdr(f'Loading {self.name}\n')
        vpn_name = self.name
        opts = self.opts
        work_dir = opts.work_dir

        #
        # acct files
        #
        accts: dict[str, Acct] = {}
        (_accts_dir, names) = get_acct_names(work_dir, vpn_name)
        for name in names:
            txt = f'  {name}\n'
            Msg.plainverb(txt, level=2)
            acct = Acct(vpn_name, name)
            # acct.name = name
            # acct.vpn_name = vpn_name
            acct.read(work_dir)
            if name != acct.name:
                Msg.warn(f'Mismatched acct name: {name} vs {acct.name}\n')
                Msg.plain(f' Changing to match filename {name}\n')
                acct.name = name
            accts[name] = acct

            #
            # mark every profile IPs as taken.
            #
            for prof in list(acct.profile.values()):
                ident = prof.ident
                if not self.vpninfo.mark_address_taken(prof.Address):
                    Msg.err(f'Error: {acct.name}:{ident.prof_name}\n')
                    self.okay = False
                    return False

        self.accts = accts

        return True

    def write_accts(self) -> bool:
        """
        Write acct data
        """
        if not self.accts:
            return True

        acct_list = list(self.accts.values())
        for acct in acct_list:
            acct.write(self.opts)
        return True

    def write_wireguard(self) -> bool:
        """
        Write all wireguard configs.
        Returns True if success.
        """
        if not self.is_active():
            return True

        opts = self.opts
        vpninfo = self.vpninfo

        wg_config = WgConfig(opts, vpninfo, self.accts)
        okay = wg_config.write_all()
        return okay

    def show_list(self):
        """
        List all accts for this vpn
        Sort by name.
        """
        opts = self.opts
        vpninfo = self.vpninfo

        if vpninfo.hidden and opts.verb < 2:
            return

        state = state_marker(vpninfo.hidden, vpninfo.active)
        mod_time = self.vpninfo.mod_time

        if not opts.brief:
            Msg.hdr(f'{state} {self.name:16s} {mod_time}:\n')

        if not self.accts:
            return

        vpn_name = self.name
        idents = opts.idents

        #
        # Idents fromt command line
        #
        accts: list[Acct] = []
        acct_names = idents.acct_names(vpn_name)

        if len(acct_names) > 0:
            acct_names = sorted(acct_names)
            for name in acct_names:
                acct = self.accts.get(name)
                if acct:
                    accts.append(acct)
                else:
                    Msg.warn(f'No such acct {name}\n')
        else:
            # all accts (sort by name)
            psorted = dict(sorted(self.accts.items()))
            accts = list(psorted.values())

        # Show them
        for acct in accts:
            acct.show_list(opts)

    def acct_prof_from_pubkey(self, pubkey_str: str) -> AcctProfile:
        """
        Locate acct, profile with matching pubkey
        """
        acct_prof = AcctProfile()

        for acct in list(self.accts.values()):
            profile = acct.prof_from_pubkey(pubkey_str)
            if profile:
                acct_prof.valid = True
                acct_prof.acct = acct
                acct_prof.profile = profile
                return acct_prof

        # no match
        return acct_prof

    def prof_from_pubkey(self, pubkey_str: str) -> Profile | None:
        """
        Locate profile with matching pubkey
        """
        for acct in list(self.accts.values()):
            profile = acct.prof_from_pubkey(pubkey_str)
            if profile:
                return profile
        return None

    def show_gw_report(self,
                       acct_prof: AcctProfile,
                       peer_rpt: PeerReport,
                       verb_level: int):
        """
        Display report for this vpn
        """
        acct = acct_prof.acct
        prof = acct_prof.profile
        ident = prof.ident

        vpninfo = self.vpninfo
        vpn_act = state_marker(vpninfo.hidden, vpninfo.active)
        acct_act = state_marker(acct.hidden, acct.active)
        prof_act = state_marker(prof.hidden, prof.active)

        gw_mark = '[gateway]' if prof.is_gw else ''

        Msg.plain('\n')
        Msg.info(f'vpn: {self.name} {vpn_act}\n')
        txt = f'{ident.prof_name} {prof_act} {gw_mark}'
        Msg.hdr(f'{acct.name} {acct_act} : {txt}\n')
        Msg.plain(f'  {"address":>12s} : {peer_rpt.allowed_ips}\n')
        Msg.plain(f'  {"endpoint":>12s} : {peer_rpt.endpoint}\n')
        Msg.plain(f'  {"handshake":>12s} : {peer_rpt.latest_handshake}\n')
        Msg.plain(f'  {"transfer":>12s} : {peer_rpt.transfer}\n')

        if verb_level > 1:
            Msg.plain(f'  {"PublicKey":>12s} : {prof.PublicKey}\n')

    def find_acct_prof(self, acct_name: str, prof_name: str
                       ) -> tuple[Acct | None, Profile | None]:
        """
        Locate exsiting acct:prof
        """
        acct = self.accts.get(acct_name)
        if not acct:
            return (None, None)

        prof: Profile | None = None
        if prof_name:
            prof = acct.find_prof(prof_name)
        return (acct, prof)

    def rename_acct(self, old_name: str, new_name: str) -> bool:
        """
        Rename acct_name -> acct_name_new
        """
        #
        # Rename acct and ensure it's profiles are
        # updated accordingly (acct_name, id_hash)
        #
        if old_name not in self.accts:
            Msg.err(f'rename_acct: no such acct {old_name}\n')
            return False

        if new_name in self.accts:
            Msg.err(f'rename_acct: acct {new_name} already exists\n')
            return False

        #
        # Update list of accts
        #
        acct = self.accts[old_name]
        self.accts[new_name] = acct
        del self.accts[old_name]

        # Ask acct to rename itself and take care of its profiles
        if not acct.rename_acct(new_name):
            return False

        #
        # Rename acct directory in
        # Data / Data_wg / vpn / <acct>
        #
        work_dir = self.opts.work_dir
        vpn_name = self.name
        if not rename_acct_dir(work_dir, vpn_name, old_name, new_name):
            return False
        return True

    def rename_prof(self,
                    acct_name: str,
                    prof_name: str,
                    prof_name_new: str) -> bool:
        """
        Rename profile acct:prof-> acct:prof_new
        """
        if acct_name not in self.accts:
            Msg.err(f'rename_prof: no such acct {acct_name}\n')
            return False

        acct = self.accts[acct_name]

        # ask acct to rename the profile
        if not acct.rename_prof(prof_name, prof_name_new):
            return False

        # rename the profile directory
        work_dir = self.opts.work_dir
        vpn_name = self.name
        if not unlink_profile(work_dir, vpn_name, acct_name, prof_name):
            return False
        return True

    def acct_exists(self, ident: Identity) -> bool:
        """
        Return true of acct exists
        """
        if ident.acct_name not in self.accts:
            return False

        acct = self.accts[ident.acct_name]
        if acct.acct_exists(ident):
            return True
        return False

    def tag_to_ident(self, tag: str) -> Identity | None:
        """
        Return the ident associated with tag
        or None if not found
        """
        ident: Identity | None = None
        for acct in list(self.accts.values()):
            ident = acct.tag_to_ident(tag)
            if ident:
                return ident
        return None

    def tag_to_prof(self, tag: str) -> Profile | None:
        """
        Return the ident associated with tag
        or None if not found
        """
        for acct in list(self.accts.values()):
            prof = acct.tag_to_prof(tag)
            if prof:
                return prof
        return None

    def tag_id_map(self) -> dict[str, str]:
        """
        Generate a dictionary of tag -> profile id string mappings
        """
        tag_id_all: dict[str, str] = {}
        for acct in list(self.accts.values()):
            tag_id = acct.tag_id_map()
            if tag_id:
                tag_id_all |= tag_id

        return tag_id_all

    def rename_vpn(self, new_name: str) -> bool:
        """
        Vpn name change
        """
        # self and vpninfo
        self.name = new_name
        if not self.vpninfo.rename_vpn(new_name):
            return False

        # accts
        for acct in list(self.accts.values()):
            if not acct.rename_vpn(new_name):
                return False
        return True

    def gateway_ids(self) -> list[str]:
        """
        Return list of gateway ids in this vpn
        """
        gw_names: list[str] = []
        for acct in list(self.accts.values()):
            names = acct.gateway_ids()
            if names:
                gw_names += names
        return gw_names

    def has_any_profiles(self) -> bool:
        """
        Returns True if vpn has any account with 1 or more profiles,
        """
        for acct in list(self.accts.values()):
            if acct.has_any_profiles():
                return True
        return False

    def pprint(self, recurs: bool = False):
        """
        Debug tool: Print myself (no dunders)
        """
        pprint(self, recurs=recurs)
