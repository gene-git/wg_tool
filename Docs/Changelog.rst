=========
Changelog
=========

Tags
====

::

	1.1.1 (2022-10-26) -> 7.5.1 (2025-08-19)
	205 commits.

Commits
=======


* 2025-08-19  : **7.5.1**

::

                update pyproject version
                update Docs/Changelogs Docs/wg_tool.pdf

* 2025-08-19  : **7.5.0**

::

                update arch PKGBUILD to 7.5.0
                Fix bug for --init. Issue #18 Reported by @Crisp-Casper
 2025-03-08     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2025-03-08  : **7.4.0**

::

                New option to set PersistentKeepAlive for user profiles.
                Sort options list printed by --help
                Update README
                Add user_keepalive (seconds) to saved options
                Server config : drop unused mod_time
 2024-12-31     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-12-31  : **7.3.0**

::

                Git tags are now signed.
                Add git signing key to Arch Package
                Bump python vers
 2024-10-22     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-10-22  : **7.2.0**

::

                Additional input protections in cidr utils
 2024-10-20     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-10-20  : **7.1.0**

::

                Use python 3 ipaddress in place of 3rd party netaddr module.
                Code reorg and some tidying
 2024-09-07     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-09-07  : **7.0.4**

::

                more readme tweaks
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-09-07  : **7.0.3**

::

                tweak RST formatting in readme
 2024-06-29     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-06-29  : **7.0.2**

::

                bug: -V,--version didnt print anything - fixed
 2024-06-28     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-06-28  : **7.0.1**

::

                Remove stray character from PKGBUILD; Add nftables dependency
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-06-28  : **7.0.0**

::

                - Split routing support via *--allowed_ips*
                    Gives ability to specify which networks use the vpn tunnel
                    New option: -aips, --allowed_ips
                    Applies to wireguard config *AllowedIps*
                    This is a string of comma separated cidr blocks or can be the word
                    *default*.
                    Default is all packets use vpn - i.e. 0.0.0.0/0,::/0
                    Option can be used with new user profile or to modify an existing
                    profile together
                    with *-mod* option.
                - general tidy ups
                - add missing contrib directory to installer scrript
                - Now uses sha3-384 to detect file changes (using python-cryptography
                module)
                  which wraps openssl
                - Update to require python 3.11 or greater
                - Restricted file permissions - new option, (*-fp, --fperms*), to ensure all
                files have appropriate
                  permissions.
                  Previous version this was always done - but it can be slow (esp. over NFS)
                  so
                  now its an option to run if needed.
 2024-04-30     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-04-30  : **6.7.7**

::

                fresh tag

* 2024-04-30  : **6.7.6**

::

                update Docs/Changelog.rst Docs/wg_tool.pdf
                Take Changelog "hack" out of PKGBUILD ... was a bad idea
 2024-04-29     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-04-29  : **6.7.5**

::

                one of those days ... another typo!
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-04-29  : **6.7.4**

::

                typo

* 2024-04-29  : **6.7.3**

::

                update Docs/Changelog.rst Docs/wg_tool.pdf
                Improve pulling latest Changelog so pacman -Qc shows it
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-04-29  : **6.7.2**

::

                PKGBUILD change to get latest Changelog
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-04-29  : **6.7.1**

::

                Update version.py as our package tooling was updated
 2024-04-23     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-04-23  : **6.7.0**

::

                Adjust for upcoming python changes.
                Some argparse options have been deprecated in 3.12 and will be removed in
                3.14
 2024-04-17     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-04-17  : **6.6.1**

::

                Package update: "pacman -Qc wg_tool" now shows the Changelog
 2024-01-19     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-19  : **6.6.0**

::

                version now includes released vs development
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-19  : **6.5.0**

::

                Remove githash from version
                Closed github issue #17.
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-19  : **6.4.0**

::

                Add --version option
 2024-01-17     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-17  : **6.3.0**

::

                Simplify ip address manipulations a few lines to original now bug is fixed
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-17  : **6.2.0**

::

                Bugfix : generating IPs was skipping too many available blocks
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-17  : **6.1.0**

::

                Fix: update AllowedIPs with --ips_refresh
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-17  : **6.0.1**

::

                bump patch version for readme change
                readme tweak
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-17  : **6.0.0**

::

                    Add support for multiple IP addresses in user profiles.
                    Addresses will now be taken from whichever networks are in server
                    config.
                    cidr address for each network will have prefixlen_4 for IPv4 and
                    prefixlen_6 for IPv6 networks.
                    prefixlen are settable with new options.
                    Existing user:profile (or -all) can have their IPs refreshed to pick up
                    their new IPs from
                    server config. If you already have multiple networks or simply added
                    them to Address variable in
                    configs/server/server.conf - then can refresh using:
                       wg-tool -mod -ips user_name:profile_name
                    or
                       wg-tool -mod -ips -all
 2024-01-13     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-13  : **5.7.2**

::

                Add ubuntu notes provided by Jack Duan (@jduan00 via github #13)
 2024-01-12     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-12  : **5.7.1**

::

                update Docs/Changelog.rst Docs/wg_tool.pdf
                lint picking
 2024-01-11     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-11  : **5.7.0**

::

                Add -upd option to update user/profile endpoint when server config changes.
                  (closes GH issue #11)
                -mod option can now be used with -all
 2024-01-07     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2024-01-07  : **5.6.3**

::

                rst fix in readme

* 2024-01-07  : **5.6.2**

::

                fix readme typo

* 2024-01-07  : **5.6.1**

::

                small readme update
 2023-12-07     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2023-12-07  : **5.6.0**

::

                wg-peer-updn now saves additional copy of wg resolv.conf in resolv.conf.wg.
                Can be used by client when resume causes network restart to overwrites the
                wg resolv.conf.
                Used by wg-client package to "fix" dns after sleep/resume.
 2023-11-23     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2023-11-23  : **5.5.1**

::

                Improve description
                update Docs/Changelog.rst Docs/wg_tool.pdf

* 2023-11-23  : **5.5.0**

::

                Change python build from poetry to hatch.
                  It is cleaner and simpler.
                Switch copyright lines to SPDX format
 2023-11-12     update Docs/Changelog.rst Docs/wg_tool.pdf

* 2023-11-12  : **5.4.1**

::

                Minor readme rst format change.
                Add wg_tool.pdf
 2023-09-30     update Docs/Changelog.rst

* 2023-09-30  : **5.3.4**

::

                Add sample output of server report to README

* 2023-09-30  : **5.3.3**

::

                Improve README
 2023-09-27     update Docs/Changelog.rst

* 2023-09-27  : **5.3.2**

::

                update Docs/Changelog.rst
                Fix links in readme.
                Remove doc build dependency on myst-parser since no more mardown
 2023-09-26     update Docs/Changelog.rst

* 2023-09-26  : **5.3.1**

::

                Release as 5.3.1
                fix rst list items in Changelog
                update Docs/Changelog.rst

* 2023-09-26  : **5.3.0**

::

                Reorg docs - add Docs/dir with sphinx support
                update PKGBUILD for optional doc builds
                Migrate to rst from markdown
 2023-09-25     update CHANGELOG.md

* 2023-09-25  : **5.1.1**

::

                README - replace markdown url links with rst link notation
 2023-08-02     update CHANGELOG.md

* 2023-08-02  : **5.1.0**

::

                Improve code finding available client IPs to properly support IPv6.
                Client IPs are chosen from the server Address list in natural order. If you
                prefer clients
                get IPv6 addresses, those should be listed first. Similarly, if IPv4 is
                preferred, then put that first.
                Tidy to keep pylint clean
 2023-07-28     update CHANGELOG.md

* 2023-07-28  : **4.7.0**

::

                Fix import open_file buglet
 2023-05-18     update CHANGELOG.md

* 2023-05-18  : **4.6.0**

::

                install: switch from pip to python installer package. This adds optimized
                bytecode
                update CHANGELOG.md

* 2023-05-18  : **4.5.3**

::

                PKGBUILD: build wheel back to using python -m build instead of poetry
 2023-05-17     update CHANGELOG.md

* 2023-05-17  : **4.5.2**

::

                Simplify Arch PKGBUILD and more closely follow arch guidelines
 2023-05-08     update CHANGELOG.md

* 2023-05-08  : **4.5.1**

::

                Add comment to README about linux using wg and ssh and MTU
 2023-05-02     typo
                update CHANGELOG.md

* 2023-05-02  : **4.5.0**

::

                Add comment on philosophy of living at the head commit.
                Change README from markdown to restructured text

* 2023-04-15  : **4.4.0**

::

                update CHANGELOG.md
                Only show user public key for "-rpt" when also using "-det".
                  Since we show user and profile name, the user key is not really needed
 2023-04-11     update CHANGELOG.md

* 2023-04-11  : **4.3.6**

::

                postup.nft script add extra line: ct status dnat accept - I saw a martial
                packat at firewall from vpn which was unexpected
                minor readme edit
                update project version
 2023-01-06     update CHANGELOG.md

* 2023-01-06  : **4.3.5**

::

                Add SPDX licensing lines
 2022-12-29     update CHANGELOG.md

* 2022-12-29  : **4.3.4**

::

                Add reminder in README to allow ip forwarding on wireguard server
 2022-12-28     update CHANGELOG.md

* 2022-12-28  : **4.3.3**

::

                Add brief networking note
 2022-12-26     update CHANGELOG.md

* 2022-12-26  : **4.3.2**

::

                Change default python interpreter location to /usr/bin/python3 (remove env).
                    This is also recommended by e.g. debian packaging guidelines
                    (https://www.debian.org/doc/packaging-manuals/python-policy). While many distros
                    (Arch, Fedora etc.) recommend /usr/bin/python - we keep python3 which will work
                    on those and on debian until debian provides python (and not just python3).
 2022-12-25     update CHANGELOG.md

* 2022-12-25  : **4.3.1**

::

                Move archlinux dir to packaging.
                Add packaging/requirements.txt
                Update build dependencies in PKGBUILD
                Tweak README
 2022-12-20     tweak README
                update CHANGELOG.md

* 2022-12-20  : **4.3.0**

::

                Change python to python3 (as per GH issue #5 on ubuntu/debian.
                Remove pip option from installer (--root-user-action=ignore)
                indent fix
                To help with older pre 3.9 python versions, provide files without match().
                They are in lib38. Copy to lib38/*.py lib/
 2022-12-14     update CHANGELOG.md

* 2022-12-14  : **4.2.0**

::

                update CHANGELOG.md
                Installer now uses pip install
                PKGBUILD now uses poetry to build wheel
 2022-12-08     update CHANGELOG.md

* 2022-12-08  : **4.1.0**

::

                Server show_rpt was not treating inactive users/profiles properly - fixed
 2022-12-04     update CHANGELOG.md

* 2022-12-04  : **4.0.0**

::

                Stronger file access permissions to protect private data in configs.
                Changes to work_dir:
                    Backward compatible with previous version.
                    Now prefers to use */etc/wireguard/wg-tool* if possible, otherwise falls
                    back to current directory.
                    Thanks to Yann Cardon
                Improve comments in postup.nft including reference to alternate postup from
                Yann Cardon
                Merge pull request #3 from ycardon/master
                Create postup-alternate.nft
                Create postup-alternate.nft
                provides an other example of postup script with useful comments
 2022-12-03     update CHANGELOG.md

* 2022-12-03  : **3.7.0**

::

                bug: --list if username(s) given without profile. Now we list all profiles
 2022-12-01     update CHANGELOG.md
                Typo in README fixed by @ycardon
                Merge pull request #2 from ycardon/master
                small typo in the readme
                small typo
                --add-users > --add_users
 2022-11-30     update CHANGELOG.md

* 2022-11-30  : **3.6.0**

::

                bug fix for --init
                Thanks to @ycardon - this fixes issue #1 : https://github.com/gene-
                git/wg_tool/issues/1
 2022-11-29     update CHANGELOG.md

* 2022-11-29  : **3.5.0**

::

                turn off test mode
                update CHANGELOG.md

* 2022-11-29  : **3.4.0**

::

                Improve wg-peer-updn
                 - Rename existing resolv.conf when saving
                 - Add timestamp to wireguard resolv.conf
                update CHANGELOG.md

* 2022-11-29  : **3.3.1**

::

                Small add to README
                update CHANGELOG.md

* 2022-11-29  : **3.3.0**

::

                Improve README
 2022-11-28     update CHANGELOG.md

* 2022-11-28  : **3.2.0**

::

                typo
                update CHANGELOG.md

* 2022-11-28  : **3.1.0**

::

                fix typo creating new user profile with -dnssrc/-dnslin
                tweak readme
                update CHANGELOG.md

* 2022-11-28  : **3.0.0**

::

                    Adds 3 new options:
                     - --mod_users : modify existing user profile (with --dns_search and
                     --dns_linux)
                     - --dns_search : adds support for dns search domain list
                     - --dns_linux : adds support for managing resolv.conf instead of
                     relying on qg-quick/resolconf
 2022-11-24     update CHANGELOG.md

* 2022-11-24  : **2.1.0**

::

                 - improve error msg
                 - Check conf before using it - added when auto updating older configs using
                 mtime of config
                 - minor tweak to bash variable check in install script
 2022-11-11     update CHANGELOG.md

* 2022-11-11  : **2.0.0**

::

                list users report now sorts by user name
                Add support for tracking config modification date-time. mod_time displayed
                in list user report
 2022-11-08     update CHANGELOG.md

* 2022-11-08  : **1.7.5**

::

                Improve handling of booelan False vs None in pre-file-write dictionary
                cleaner
 2022-11-07     update CHANGELOG.md

* 2022-11-07  : **1.7.4**

::

                tweak readme
 2022-11-04     update CHANGELOG.md

* 2022-11-04  : **1.7.3**

::

                add poetry back to PKGBUILD makedepends
                update CHANGELOG.md

* 2022-11-04  : **1.7.2**

::

                change installer to use bash array for app list (even tho we onlly have 1
                here)
                tweak readme
 2022-10-31     update CHANGELOG.md

* 2022-10-31  : **1.7.1**

::

                Change build from poetry/pip to python -m build/installer
                update CHANGELOG.md

* 2022-10-31  : **1.7.0**

::

                Add support for python 3.11 tomllib
 2022-10-30     update CHANGELOG.md

* 2022-10-30  : **1.6.1**

::

                update readme
                update CHANGELOG.md

* 2022-10-30  : **1.6.0**

::

                -rpt now lists missing users/profiles from running server
                update CHANGELOG.md

* 2022-10-30  : **1.5.0**

::

                Add --details
                Modifes -l, -rpt and -rrpt to provide detailed information in addition to
                the summary.
 2022-10-29     update CHANGELOG.md

* 2022-10-29  : **1.4.0**

::

                report: handle cases where running server has old user key and other edge
                cases
                update CHANGELOG.md

* 2022-10-29  : **1.3.2**

::

                add --run_show_rpt. Similar to --show_rpt, but runs wg-tool
                update CHANGELOG.md

* 2022-10-29  : **1.3.1**

::

                bug fix: -inact user:prof made user inactive not just prof
                update CHANGELOG.md

* 2022-10-29  : **1.3.0**

::

                Add new option --work_dir
                Refactor and tidy code up some
 2022-10-28     upd changelog
                tweak readme
 2022-10-27     tweak readme and sync PKGBUILD
                upd changelog

* 2022-10-27  : **1.2.3**

::

                Add mising packages to PKGBUILD depends (thank you @figue on aur)
                upd changelog

* 2022-10-27  : **1.2.2**

::

                duh - turn off debugger .. sorry
                markdown newline fix
                word smith readme
 2022-10-26     update changelog

* 2022-10-26  : **1.2.1**

::

                update project vers
                actually add the code to make wg_show report :)

* 2022-10-26  : **1.2.0**

::

                Adds support to parse output of wg show and provide user/profile names
                Add new/coming soon section to readme
                readme - aur package now avail
                update changelog

* 2022-10-26  : **1.1.1**

::

                proj vers update
                installer: share archlinux into /usr/share/wg_tool
                Ready to share


