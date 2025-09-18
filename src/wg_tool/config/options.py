# SPDX-25License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
# PYTHON_ARGCOMPLETE_OK
"""
Options - command line options for WgTool
"""
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
from typing import (Any)
import os
import argparse

from utils import Msg
from utils import csv_string_to_list

from .options_save import (read_saved_options, write_saved_options)
from .completion import completion_init

type _Opt = tuple[str | tuple[str, ...], dict[str, Any]]


def _title_underline(title: str) -> str:
    """
    Argparse appends ":" - pretty this up a bit
    """
    n = len(title)
    lines = ':*' + n * '-' + '*'
    title = f'{lines}:\n: {title} :\n{lines}'
    return title


def _migrate_options() -> tuple[str, str, list[_Opt]]:
    """
    Migrate Group of options
    """
    opts: list[_Opt] = []

    title = _title_underline('Migrate & Import Options')
    description = 'Migrating from versions prior to 8.0.'

    txt = 'Migrate database from pre v8.0 version:\n'
    txt += 'configs -> Data, wg-configs -> Data-wg\n'
    txt += 'Legacy directories are unchanged\n'
    opts.append((('-migrate', '--migrate'),
                 {'action': 'store_true', 'help': txt}))

    txt = 'Import standard wireguard configs.\n'
    txt += ' The vpn must exist with matching and networks\n'
    txt += ' All configs should be in the work dir and\n'
    txt += ' the path to each config file should be:\n'
    txt += '     <vpn-name>/<account-name>/<profile-name>.conf\n'
    opts.append((('-import-configs', '--import-configs'),
                 {'metavar': '<vpn-name>', 'help': txt}))

    return (title, description, opts)


def _positional_options() -> tuple[str, str, list[_Opt]]:
    """
    Positional args
    """
    opts: list[_Opt] = []

    title = _title_underline('Positional Arguments')
    description = 'One or more identity names ID(s)'

    txt = ('<vpn>.<account>.<profile> ...'
           '\ne.g. client :\tvpn1.bob.laptop'
           '\ne.g. gateway:\tvpn1.servers:gateway-1'
           '\nNB Some options may take <vpn>.<account> or just <vpn>'
           )
    opts.append(('ident_names',
                {'nargs': '*', 'help': txt, 'metavar': 'id_names', }))

    return (title, description, opts)


def _edit_options() -> tuple[str, str, list[_Opt]]:
    """
    Edit Group of options
    Booleans:
        implied: modify = True (means use mods/xxx)
            --edit
            --copy
            --new
            --merge
            --rename
         modify = False  (means not using mods/xxx)
            --roll-keys
            --active
            --not-active
            --hidden
            --not-hidden
     Companion options:
        --ident
        --to-idend
    """
    opts: list[_Opt] = []

    title = _title_underline('Edit / Modify Options')
    description = 'Add, edit or modify identities.'

    txt = 'Edit one item.\n'
    txt += 'Requires --ident "vpn.account.profile"'
    opts.append((('-edit', '--edit'),
                 {'help': txt, 'action': 'store_true'}))

    txt = 'Copy one identity to another.\n'
    txt += 'Requires --ident <from> --to-ident <to>'
    opts.append((('-copy', '--copy'),
                 {'help': txt, 'action': 'store_true'}))

    txt = 'Rename an identity.\n'
    txt += 'Requires --ident and --to-ident'
    opts.append((('-rename', '--rename'),
                 {'help': f'{txt}', 'action': 'store_true'}))

    txt = 'Specify an identity.\n'
    txt += 'Use with --edit, --copy and --rename)'
    opts.append((('-ident', '--ident'),
                 {'help': txt, 'metavar': 'vpn.account.prof'}))

    txt = 'Specify target identity,\n'
    txt += 'Use with: --copy and --rename)'
    opts.append((('-to-ident', '--to-ident'),
                 {'help': txt, 'metavar': 'vpn.account.prof'}))

    txt = 'Merge edits from a file.'
    opts.append((('-merge', '--merge'),
                 {'metavar': 'FILE', 'help': txt}))

    # Add/Remove wanted networks
    txt = 'Add wanted network(s) to IDs (See positional parameters)\n'
    txt += 'Multiple networks use comma separated list\n'
    txt += 'Special network "internet" is same as internet_wanted = true'
    opts.append((('-nets-wanted-add', '--nets-wanted-add'),
                 {'help': txt}))

    txt = 'Delete wanted network(s) from IDs (See positional parameters)\n'
    txt += 'Multiple networks as comma separated list\n'
    txt += 'Special network "internet" is same as internet_wanted = false'
    opts.append((('-nets-wanted-del', '--nets-wanted-del'),
                 {'help': txt}))

    # Add/Remove offered networks
    txt = 'Add offered network(s) to IDs (See positional parameters)\n'
    txt += 'Multiple networks use comma separated list\n'
    txt += 'Special network "internet" is same as internet_offered = true'
    opts.append((('-nets-offered-add', '--nets-offered-add'),
                 {'help': txt}))

    txt = 'Delete offered network(s) from IDs (See positional parameters)\n'
    txt += 'Multiple networks as comma separated list\n'
    txt += 'Special network "internet" is same as internet_offered = false'
    opts.append((('-nets-offered-del', '--nets-offered-del'),
                 {'help': txt}))

    txt = 'Create new item (See positional parameters))]\n'
    txt += 'Each can be one of: vpn, vpn.account or vpn.account.prof'
    opts.append((('-new', '--new'),
                 {'help': txt, 'action': 'store_true'}))

    txt = 'Generate new keys for IDs (See positional parameters)'
    opts.append((('-roll', '--roll-keys'),
                 {'action': 'store_true', 'help': txt}))

    txt = 'Mark some IDs active. (Use positional parameters)'
    opts.append((('-active', '--active'),
                 {'action': 'store_true', 'help': txt}))

    txt = 'Mark some IDs not active. (See positional parameters)'
    opts.append((('-not-active', '--not-active'),
                 {'action': 'store_true', 'help': txt}))

    txt = 'Mark some hidden. (Use positional parameters)'
    txt = 'Hidden are not shown unless double verb -vv is used.'
    opts.append((('-hidden', '--hidden'),
                 {'action': 'store_true', 'help': txt}))

    txt = 'Mark some IDs not hidden. (See positional parameters)\n'
    opts.append((('-not-hidden', '--not-hidden'),
                 {'action': 'store_true', 'help': txt}))

    #
    # Sort options alphabetically
    #   - Sort on first as some may only have one option.
    #
    # opts.sort(key=lambda item: item[0][0])

    return (title, description, opts)


def _stored_options(saved: dict[str, Any]) -> tuple[str, str, list[_Opt]]:
    """
    Stored Group of options
    """
    opts: list[_Opt] = []

    title = _title_underline('Stored Options')
    description = 'These are saved as new default values.'

    #
    # Options that can be saved
    #
    default = '5'
    if saved and saved.get('hist'):
        default = str(saved['hist'])

    txt = f'Number of previous data configs to retain ({default})'
    opts.append((('-hist', '--hist'),
                 {'metavar': 'NUM', 'default': default, 'help': txt}))

    default = '3'
    if saved and saved.get('hist_wg'):
        default = str(saved['hist_wg'])

    txt = f'Number of previous wireguard configs to retain ({default})'
    opts.append((('-hist-wg', '--hist-wg'),
                 {'metavar': 'NUM', 'default': default, 'help': txt}))

    # toggle = True
    # if saved and saved.get('net_compact') is not None:
    #     toggle = saved['net_compact']

    # txt = 'Compact networks output in AllowedIPs'
    # opts.append((('-net-compact', '--net-compact'),
    #              {'action': 'store_true', 'default': toggle,
    #               'help': txt + f' ({toggle})'}))

    # txt = 'Do NOT ' + txt
    # opts.append((('-no-net-compact', '--no-net-compact'),
    #              {'action': 'store_false', 'dest': 'net_compact',
    #               'help': txt}))

    return (title, description, opts)


def _report_options() -> tuple[str, str, list[_Opt]]:
    """
    Reporting options.
    """
    opts: list[_Opt] = []

    title = _title_underline('Reporting Options')
    description = 'Peer info and reports from wg server report'

    txt = 'List vpns, accounts & profiles. May filter by providing IDs\n'
    txt += 'profile names may comma separated list\n'
    txt += 'e.g.\n'
    txt += '  all : -l\n'
    txt += '  all accounts and profiles of "vpn1": -l vpn1\n'
    txt += '  all profiles of "vpn1.bob": -l vpn1.bob\n'
    txt += '  2 profiles of "vpn1.bob": -l vpn1.bob.prof-1,prof-2\n'

    opts.append((('-l', '--list',),
                 {'action': 'store_true', 'help': txt}))

    txt = ('Generate report from "wg show" output (file or "stdin")'
           ' (See also --run-show-report)'
           )
    opts.append((('-rpt',  '--show-rpt'),
                 {'help': txt, 'metavar': 'RPTFILE'}))

    txt = ('Run "wg show" (must be on wireguard server) and generate report.'
           ' (See also --show-rpt)'
           )
    opts.append((('-rrpt',  '--run-show-rpt'),
                 {'action': 'store_true', 'help': txt}))

    txt = 'Simplified outputs. Opposite of -det'
    opts.append((('-b', '--brief',),
                 {'action': 'store_true', 'help': txt}))

    #
    # Sort alphabetically on first as some may only have one option.
    #
    # opts.sort(key=lambda item: item[0][0])

    return (title, description, opts)


def _general_options() -> tuple[str, str, list[_Opt]]:
    """
    Manage command line options (argparse)
    """
    opts: list[_Opt] = []

    title = _title_underline('General Options')
    description = 'Miscellaneous options.'

    txt = ('Force a refresh and write all wireguard configs.'
           '\nThis is automatic and is not needed normally.'
           )
    opts.append((('-r', '--refresh'),
                 {'action': 'store_true', 'help': txt}))

    txt = 'Redo restricted file permissions on all data files.'
    txt += ' Not normally needed.'
    opts.append((('-fp', '--file-perms'),
                 {'action': 'store_true', 'help': txt}))

    txt = 'Verbose output. Repeat for even more verbosity.\n'
    txt += '-vv works with -l and -rpt. Use -vvv for very verbose output'
    opts.append((('-v', '--verb'),
                 {'action': 'count', 'default': 0, 'help': txt}))

    # txt = 'When applicable, apply action to this vpn name.'
    # opts.append((('-vpn', '--vpn-name'),
    #              {'help': txt}))

    opts.append((('-V', '--version'),
                 {'action': 'store_true', 'help': 'Version info'}))

    #
    # Sort alphabetically on first as some may only have one option.
    #
    # opts.sort(key=lambda item: item[0][0])

    return (title, description, opts)


def parse_args(work_dir: str, data_dir: str) -> dict[str, Any]:
    """
    Command line options
     - some may be optionally saved to file in config dir
     - 2 parsing phases:
       - phase 1: parse work_dir
       - phase 2: use work_dir for remaining options.
    """
    groups: list[tuple[argparse._ArgumentGroup, list[_Opt]]] = []
    desc: str = 'wg-tool: Manage wireguard config files'

    #
    # Phase 1: "work_dir" option.
    #  -> load saved options using work_dir
    #  -> handle all remaining options.
    #
    par1 = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.RawTextHelpFormatter
            )

    txt = f'Set the working directory path ({work_dir})'
    par1.add_argument("-wkd", "--work-dir",
                      default=work_dir, metavar='DIR', help=txt)

    par2 = argparse.ArgumentParser(
            description=desc,
            add_help=True,
            formatter_class=argparse.RawTextHelpFormatter,
            parents=[par1])

    wkd_args, rest_args = par1.parse_known_args()
    if wkd_args.work_dir:
        work_dir = wkd_args.work_dir

    #
    # read any saved options using latest work_dir.
    #
    saved_path = os.path.join(work_dir, data_dir, 'saved_options')
    saved = read_saved_options(saved_path)

    #
    # Phase 2: Handle rest of the options
    #
    _initialize_groups(saved, par2, groups)

    #
    # Parse and return dictionary
    # Note:
    #   python 3.12 deprecated some argparse options like 'type': int
    #   - So we only use bool/str/list[str] options.
    #
    option_dict: dict[str, Any] = {}
    saved_option_dict: dict[str, Any] = {}

    completion_init(par2)
    args = par2.parse_args(rest_args, namespace=wkd_args)

    #
    # Current remaining options
    #
    if args:
        int_keys = ('hist', 'hist_wg')
        cslist_keys = ('nets_wanted_add', 'nets_wanted_del',
                       'nets_offered_add', 'nets_offered_del')
        save_keys = int_keys
        for (key, val) in vars(args).items():
            if val is not None:

                if key in int_keys:
                    option_dict[key] = int(val)

                elif key in cslist_keys:
                    option_dict[key] = csv_string_to_list(val)

                else:
                    option_dict[key] = val

                if key in save_keys:
                    saved_option_dict[key] = option_dict[key]

        # tidy import-config name
        import_dir = option_dict.get('import_configs')
        if import_dir:
            if import_dir[-1] == '/':
                import_dir = import_dir[0:-1]
            if import_dir[0:2] == './':
                import_dir = import_dir[2:]
            option_dict['import_configs'] = import_dir
    #
    # Updated saved_option file if needed.
    #
    if ((not saved and saved_option_dict)
            or (saved_option_dict and saved != saved_option_dict)):
        if not write_saved_options(saved_option_dict, saved_path):
            Msg.err(f'Error saving options to {saved_path}\n')
            return option_dict
    return option_dict


def _initialize_groups(
        saved: dict[str, Any],
        par2: argparse.ArgumentParser,
        groups: list[tuple[argparse._ArgumentGroup, list[_Opt]]]):
    """
    Initialize all available option gropus
    """
    (title, desc, positional) = _positional_options()
    group_positional = par2.add_argument_group(title, desc)
    groups.append((group_positional, positional))

    (title, desc, migrate) = _migrate_options()
    group_migrate = par2.add_argument_group(title, desc)
    groups.append((group_migrate, migrate))

    (title, desc, edit) = _edit_options()
    group_edit = par2.add_argument_group(title, desc)
    groups.append((group_edit, edit))

    (title, desc, report) = _report_options()
    group_report = par2.add_argument_group(title, desc)
    groups.append((group_report, report))

    (title, desc, general) = _general_options()
    group_general = par2.add_argument_group(title, desc)
    groups.append((group_general, general))

    (title, desc, stored) = _stored_options(saved)
    group_stored = par2.add_argument_group(title, desc)
    groups.append((group_stored, stored))

    for item in groups:
        group = item[0]
        opts = item[1]

        for opt in opts:
            opt_list, kwargs = opt
            if isinstance(opt_list, str):
                group.add_argument(opt_list, **kwargs)
            else:
                group.add_argument(*opt_list, **kwargs)
