.. SPDX-License-Identifier: GPL-2.0-or-later

.. _Options-section:

Command Line Options
====================

As usual the help message is available via:

.. code-block::

   wg-tool --help

Which prints a list of available options.

Some items may be modified using *--edit* and some, like *--rename* have not 
edit counterpart.

Sometimes it may be more convenient to use an option rather than edit.


Current Help
------------

.. code-block:: text


    usage: wg-tool [-h] 
                   [-wkd DIR] 
                   [-migrate] 
                   [-import-configs <vpn-name>] 
                   [-edit]
                   [-copy] 
                   [-rename] 
                   [-ident vpn.account.prof]
                   [-to-ident vpn.account.prof] 
                   [-merge FILE]
                   [-nets-wanted-add NETS_WANTED_ADD]
                   [-nets-wanted-del NETS_WANTED_DEL]
                   [-nets-offered-add NETS_OFFERED_ADD]
                   [-nets-offered-del NETS_OFFERED_DEL] 
                   [-new] 
                   [-roll] 
                   [-active]
                   [-not-active] 
                   [-hidden] 
                   [-not-hidden] 
                   [-l] 
                   [-rpt RPTFILE]
                   [-rrpt] 
                   [-b] 
                   [-r] 
                   [-fp] 
                   [-v] 
                   [-V] 
                   [-hist NUM] 
                   [-hist-wg NUM]
                   [id_names ...]

    wg-tool: Manage wireguard config files

    options:
      -h, --help            show this help message and exit
      -wkd, --work-dir DIR  Set the working directory path (./)

    :*--------------------*:
    : Positional Arguments :
    :*--------------------*:
      One or more identity names ID(s)

      id_names              <vpn>.<account>.<profile> ...
                            e.g. client :	vpn1.bob.laptop
                            e.g. gateway:	vpn1.servers:gateway-1
                            NB Some options may take <vpn>.<account> or just <vpn>

    :*------------------------*:
    : Migrate & Import Options :
    :*------------------------*:
      Migrating from versions prior to 8.0.

      -migrate, --migrate   Migrate database from pre v8.0 version:
                            configs -> Data, wg-configs -> Data-wg
                            Legacy directories are unchanged
      -import-configs, --import-configs <vpn-name>
                            Import standard wireguard configs.
                             The vpn must exist with matching and networks
                             All configs should be in the work dir and
                             the path to each config file should be:
                                 <vpn-name>/<account-name>/<profile-name>.conf

    :*---------------------*:
    : Edit / Modify Options :
    :*---------------------*:
      Add, edit or modify identities.

      -edit, --edit         Edit one item.
                            Requires --ident "vpn.account.profile"
      -copy, --copy         Copy one identity to another.
                            Requires --ident <from> --to-ident <to>
      -rename, --rename     Rename an identity.
                            Requires --ident and --to-ident
      -ident, --ident vpn.account.prof
                            Specify an identity.
                            Use with --edit, --copy and --rename)
      -to-ident, --to-ident vpn.account.prof
                            Specify target identity,
                            Use with: --copy and --rename)
      -merge, --merge FILE  Merge edits from a file.
      -nets-wanted-add, --nets-wanted-add NETS_WANTED_ADD
                            Add wanted network(s) to IDs (See positional parameters)
                            Multiple networks use comma separated list
                            Special network "internet" is same as internet_wanted = true
      -nets-wanted-del, --nets-wanted-del NETS_WANTED_DEL
                            Delete wanted network(s) from IDs (See positional parameters)
                            Multiple networks as comma separated list
                            Special network "internet" is same as internet_wanted = false
      -nets-offered-add, --nets-offered-add NETS_OFFERED_ADD
                            Add offered network(s) to IDs (See positional parameters)
                            Multiple networks use comma separated list
                            Special network "internet" is same as internet_offered = true
      -nets-offered-del, --nets-offered-del NETS_OFFERED_DEL
                            Delete offered network(s) from IDs (See positional parameters)
                            Multiple networks as comma separated list
                            Special network "internet" is same as internet_offered = false
      -new, --new           Create new item (See positional parameters))]
                            Each can be one of: vpn, vpn.account or vpn.account.prof
      -roll, --roll-keys    Generate new keys for IDs (See positional parameters)
      -active, --active     Mark some IDs active. (Use positional parameters)
      -not-active, --not-active
                            Mark some IDs not active. (See positional parameters)
      -hidden, --hidden     Hidden are not shown unless double verb -vv is used.
      -not-hidden, --not-hidden
                            Mark some IDs not hidden. (See positional parameters)

    :*-----------------*:
    : Reporting Options :
    :*-----------------*:
      Peer info and reports from wg server report

      -l, --list            List vpns, accounts & profiles. May filter by providing IDs
                            profile names may comma separated list
                            e.g.
                              all : -l
                              all accounts and profiles of "vpn1": -l vpn1
                              all profiles of "vpn1.bob": -l vpn1.bob
                              2 profiles of "vpn1.bob": -l vpn1.bob.prof-1,prof-2
      -rpt, --show-rpt RPTFILE
                            Generate report from "wg show" output (file or "stdin") (See also --run-show-report)
      -rrpt, --run-show-rpt
                            Run "wg show" (must be on wireguard server) and generate report. (See also --show-rpt)
      -b, --brief           Simplified outputs. Opposite of -det

    :*---------------*:
    : General Options :
    :*---------------*:
      Miscellaneous options.

      -r, --refresh         Force a refresh and write all wireguard configs.
                            This is automatic and is not needed normally.
      -fp, --file-perms     Redo restricted file permissions on all data files. Not normally needed.
      -v, --verb            Verbose output. Repeat for even more verbosity.
                            -vv works with -l and -rpt. Use -vvv for very verbose output
      -V, --version         Version info

    :*--------------*:
    : Stored Options :
    :*--------------*:
      These are saved as new default values.

      -hist, --hist NUM     Number of previous data configs to retain (5)
      -hist-wg, --hist-wg NUM
                            Number of previous wireguard configs to retain (3)

.. _Compacting:

Compacting Networks
-------------------

Note on networks. The wireguard config *AllowedIPs* variable compacts
networks to  the minimal list of CIDRs. For convenience, the
pre-compacted list of networks is provided as a comment.

For example:

.. code-block:: none

    [10.77.77.1/32, 0.0.0.0/0, 192.168.1.0/24, ::/0, fc00:77:77::1/128]

    gets compacted to → 

    [0.0.0.0/0, ::/0]

since *192.168.1.0/24* is a subnet of *0.0.0.0/0* and similarly for the IPv6 net.

A comment is added to the config file which shows all the *AllowedIPs*
networks prior to compacting. This can be helpful when looking them over for 
testing or checking purposes.

