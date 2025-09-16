# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Output from 'wg show'
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-branches
import sys

from utils import Msg
from utils import state_marker
from utils import open_file
from utils import run_prog

from .acct_prof import AcctProfile


class PeerReport:
    """
    Report data for one peer
    """
    def __init__(self):
        # Pure Peers
        self.pubkey: str = ''
        self.endpoint: str = ''
        self.allowed_ips: str = ''
        self.latest_handshake: str = ''
        self.transfer: str = ''

        # gateway
        self.interface: str = ''
        self.listening_port: str = ''

        # identifed data
        self.acct_prof: AcctProfile = AcctProfile()

    def display(self, verb_level: int):
        """
        Display this peer
        """
        if not self.acct_prof.valid:
            return

        acct = self.acct_prof.acct
        prof = self.acct_prof.profile
        ident = prof.ident

        gw_mark = '(gateway)' if prof.is_gw else ''

        acct_act = state_marker(acct.hidden, acct.active)
        prof_act = state_marker(acct.hidden, prof.active)

        # gateway
        Msg.plain('\n')
        txt = f'{ident.prof_name} {prof_act} {gw_mark}'
        Msg.hdr(f'{acct.name} {acct_act} : {txt}\n')

        if self.interface:
            Msg.plain(f'  {"interface":>18s} : {self.interface}\n')

        if self.listening_port:
            Msg.plain(f'  {"listen_port":>18s} : {self.listening_port}\n')

        if prof.AddressWg:
            Msg.plain(f'  {"address":>18s} : {prof.AddressWg}\n')

        if self.allowed_ips:
            Msg.plain(f'  {"allowed_ips":>18s} : {self.allowed_ips}\n')

        if self.endpoint:
            Msg.plain(f'  {"endpoint":>18s} : {self.endpoint}\n')

        if self.latest_handshake:
            Msg.plain(f'  {"handshake":>18s} : {self.latest_handshake}\n')

        if self.transfer:
            Msg.plain(f'  {"transfer":>18s} : {self.transfer}\n')

        if verb_level > 1:
            return

        if prof.internet_offered:
            txt = str(prof.internet_offered)
            Msg.plain(f'  {"internet_offered":>18s} : {txt}\n')

        if prof.internet_wanted:
            txt = str(prof.internet_wanted)
            Msg.plain(f'  {"internet_wanted":>18s} : {txt}\n')

        if prof.nets_offered:
            Msg.plain(f'  {"nets_offered":>18s} : {prof.nets_offered}\n')

        if prof.nets_wanted:
            Msg.plain(f'  {"nets_wanted":>18s} : {prof.nets_wanted}\n')

        Msg.plain(f'  {"PublicKey":>18s} : {prof.PublicKey}\n')


class GwReport:
    """
    Organize output of wg show
    """
    # def __init__(self, data_rows: list[str]):
    def __init__(self, rpt_from: str):
        """
        Parse the output:
        interface: <name>
          public key: <xxx>
          private key: (hidden)
          listening port: NNN

        peer: <pubkey>
            preshared key: (hidden)
            endpoint: xxx:xxx
            allowed ips: xxx
            latest handshare: ...
            transfer: xxxx

        peer; ...
        """
        self.okay: bool = True

        self.gateway: PeerReport = PeerReport()
        self.wg_peer: list[PeerReport] = []

        # read the data
        (okay, rows) = _read_data(rpt_from)
        if not okay:
            self.okay = False
            return

        # parse it
        _parse_data(self, rows)


def _read_data(rpt_from: str) -> tuple[bool, list[str]]:
    """
    Read data from file / stdin or  run 'wg show'

    Args:
        rpt_from (str):
            Where to read report
            stdin, file or run the report

    Returns:
        tuple[success: bool, list[rows: str]]:
            True if read data.
            List of data rows.
    """
    rows: list[str] = []
    data: str = ''
    if not rpt_from:
        Msg.err('No wg report source')
        return (False, rows)

    if rpt_from == 'run':
        (okay, rows) = _run_wg_rpt()
        if not okay:
            return (False, rows)

    elif rpt_from == 'stdin':
        data = sys.stdin.read()

    else:
        fob = open_file(rpt_from, 'r')
        if fob:
            data = fob.read()
            fob.close()
        else:
            Msg.err(f'Error reading rpt file: {rpt_from}')
            return (False, rows)

    if data:
        rows = data.splitlines()
    return (True, rows)


def _run_wg_rpt() -> tuple[bool, list[str]]:
    """
    Run the report
    """
    data: list[str] = []

    pargs = ['/usr/bin/wg', 'show']
    (retc, output, errors) = run_prog(pargs)
    if retc != 0:
        Msg.err('Failed to run "wg show"\n')
        Msg.plain(errors)
        return (False, data)

    if output:
        data = output.splitlines()
    return (True, data)


def _parse_data(wg_rpt: GwReport, rows: list[str]):
    """
    Parse out what we need
    1 interface and 0 or more peers.
    interface is always first.
    """
    attribs = {
            'interface': 'interface',
            'public key': 'pubkey',
            'listening port': 'listening_port',
            'endpoint': 'endpoint',
            'allowed ips': 'allowed_ips',
            'latest handshake': ' latest_handshake',
            'transfer': 'transfer',
            'peer': 'pubkey',
            }

    gateway_keys = ('interface', 'public key', 'listening port')
    peer_keys = ('peer', 'endpoint', 'allowed ips',
                 'latest handshake', 'transfer')

    interface_done: bool = False
    gateway = wg_rpt.gateway

    for row in rows:
        rowc = row.strip()
        if not rowc:
            continue

        (key, _delim, val) = rowc.partition(':')
        if key:
            key = key.strip()
        if val:
            val = val.strip()

        if key == 'peer':
            interface_done = True
            acct_prof = AcctProfile()
            acct_prof.valid = True
            wg_peer = PeerReport()
            wg_peer.acct_prof = acct_prof
            wg_rpt.wg_peer.append(wg_peer)

        if not interface_done and key in gateway_keys:
            attrib = attribs[key]
            setattr(gateway, attrib, val)
            continue

        if interface_done and acct_prof.valid and key in peer_keys:
            attrib = attribs[key]
            setattr(wg_peer, attrib, val)
            continue
