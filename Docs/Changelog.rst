Changelog
=========

[5.3.0] ----- 2023-09-26
 * update project version  
 * PKGBUILD - move doc building depnds to makedepends - uncomment to use  
 * update Changelog.rst  

[5.2.0] ----- 2023-09-26
 * update project version  
 * Fix PKGBUILD for optdepends where colon has no whitespace in front xxx: xxx  
 * update PKGBUILD for optional doc builds  
 * Reorg docs - add Docs/dir with sphinx support  
 * update CHANGELOG.md  

[5.1.1] ----- 2023-09-25
 * update project version  
 * README - replace markdown url links with rst link notation  
 * update CHANGELOG.md  

[5.1.0] ----- 2023-08-02
 * update project version  
 * Tidy to keep pylint clean  
 * update CHANGELOG.md  

[5.0.0] ----- 2023-08-02
 * update project version  
 * Improve code finding available client IPs to properly support IPv6.  
   Client IPs are chosen from the server Address list in natural order. If you prefer clients  
   get IPv6 addresses, those should be listed first. Similarly, if IPv4 is preferred, then put that first.  
 * update CHANGELOG.md  

[4.7.0] ----- 2023-07-28
 * update project version  
 * Fix import open_file buglet  
 * update CHANGELOG.md  

[4.6.0] ----- 2023-05-18
 * update project version  
 * install: switch from pip to python installer package. This adds optimized bytecode  
 * update CHANGELOG.md  

[4.5.3] ----- 2023-05-18
 * update project version  
 * PKGBUILD: build wheel back to using python -m build instead of poetry  
 * update CHANGELOG.md  

[4.5.2] ----- 2023-05-17
 * update project version  
 * Simplify Arch PKGBUILD and more closely follow arch guidelines  
 * update CHANGELOG.md  

[4.5.1] ----- 2023-05-08
 * update project version  
 * Add comment to README about linux using wg and ssh and MTU  
 * typo  
 * update CHANGELOG.md  

[4.5.0] ----- 2023-05-02
 * update project version  
 * fix pyproject to use README.rst  
 * Add comment on philosophy of living at the head commit.  
   Change README from markdown to restructured text  
 * update CHANGELOG.md  

[4.4.0] ----- 2023-04-15
 * update project version  
 * Only show user public key for "-rpt" when also using "-det".  
   Since we show user and profile name, the user key is not really needed  
 * update CHANGELOG.md  

[4.3.6] ----- 2023-04-11
 * update project version  
 * minor readme edit  
 * postup.nft script add extra line: ct status dnat accept - I saw a martial packat at firewall from vpn which was unexpected  
 * update CHANGELOG.md  

[4.3.5] ----- 2023-01-06
 * update project version  
 * Add SPDX licensing lines  
 * update CHANGELOG.md  

[4.3.4] ----- 2022-12-29
 * update project version  
 * Add reminder in README to allow ip forwarding on wireguard server  
 * update CHANGELOG.md  

[4.3.3] ----- 2022-12-28
 * update project version  
 * Add brief networking note  
 * update CHANGELOG.md  

[4.3.2] ----- 2022-12-26
 * update project version  
 * Change default python interpreter location to /usr/bin/python3 (remove env).  
   This is also recommended by e.g. debian packaging guidelines (https://www.debian.org/doc/packaging-manuals/python-policy). While many distros (Arch, Fedora etc.) recommend /usr/bin/python - we keep python3 which will work on those and on debian until debian provides python (and not just python3).  
 * update CHANGELOG.md  

[4.3.1] ----- 2022-12-25
 * update project version  
 * update CHANGELOG.md  
 * update project version  
 * Move archlinux dir to packaging.  
   Add packaging/requirements.txt  
   Update build dependencies in PKGBUILD  
   Tweak README  
 * tweak README  
 * update CHANGELOG.md  

[4.3.0] ----- 2022-12-20
 * update project version  
 * Change python to python3 (as per GH issue #5 on ubuntu/debian  
 * indent fix  
 * update changelog  
 * To help with older pre 3.9 python versions, provide files without match()  
 * update CHANGELOG.md  

[4.2.0] ----- 2022-12-14
 * update project version  
 * readme - change build to poetry  
 * try quieten pip more  
 * typo  
 * installer now used pip install in place of python -m installer.  
   PKGBUILD now uses poetry to build the wheel package.  
 * update CHANGELOG.md  

[4.1.0] ----- 2022-12-08
 * update project version  
 * Server show_rpt was not treating inactive users/profiles properly - fixed  
 * update CHANGELOG.md  

[4.0.0] ----- 2022-12-04
 * update project version  
 * Stronger file access permissions to protect private data in configs.  
   Changes to work_dir.  
   Backward compatible with previous version.  
   Now prefers to use */etc/wireguard/wg-tool* if possible, otherwise falls back to current directory.  
 * More restrictive permissions on config files  
 * Improve comments in postup.nft  
 * Alternative postup nft script from Yann Cardon  
 * update CHANGELOG.md  

[3.7.0] ----- 2022-12-03
 * update project version  
 * bug: --list if username(s) given without profile. Now we list all profiles  
 * PKGBUILD comment has wrong package name  
 * update changelog  
 * Typo in README fixed by @ycardon  
 * update CHANGELOG.md  

[3.6.0] ----- 2022-11-30
 * update project version  
 * bug fix for --init  
   Thanks to @ycardon - this fixes issue #1 : https://github.com/gene-git/wg_tool/issues/1  
 * update CHANGELOG.md  

[3.5.0] ----- 2022-11-29
 * update project version  
 * test mode off  
 * update CHANGELOG.md  

[3.4.0] ----- 2022-11-29
 * update project version  
 * Improve wg-peer-updn  
   - Rename existing resolv.conf when saving  
   - Add timestamp to wireguard resolv.conf  
 * update CHANGELOG.md  

[3.3.1] ----- 2022-11-29
 * update project version  
 * small add to readme  
 * update CHANGELOG.md  

[3.3.0] ----- 2022-11-29
 * update project version  
 * More work on README  
 * update CHANGELOG.md  

[3.2.0] ----- 2022-11-28
 * update project version  
 * no debug  
 * goofy typo ...  
 * update CHANGELOG.md  

[3.1.0] ----- 2022-11-28
 * update project version  
 * fix bug creating new user with -dnssrch/-dnslin not taking  
 * tiny change in new section  
 * update CHANGELOG.md  

[3.0.0] ----- 2022-11-28
 * update project version  
 * typo in installer script  
 * keep /etc/wireguard 700  
 * fix installer for wg-peer-updn  
 * renamed post up/down script to wg-peer-updn  
 * tweak readme  
 * Install scripts/wg-peer-updn to /etc/wireguard/scripts  
 * word smith README  
 * Adds 3 new options:  
   - --mod_users : modify existing user profile (with --dns_search and --dns_linux)  
   - --dns_search : adds support for dns search domain list  
   - --dns_linux : adds support for managing resolv.conf instead of relying on qg-quick/resolconf  
 * update CHANGELOG.md  
 * update project version  
 * update CHANGELOG.md  
 * update CHANGELOG.md  

[2.1.0] ----- 2022-11-24
 * update project version  
 * improve error msg  
 * improve error msg  
 * Check conf before using it - added when auto updating older configs using mtime of config  
 * minor tweak to bash variable check in install script  
 * update CHANGELOG.md  

[2.0.0] ----- 2022-11-11
 * update project version  
 * improve list users report  
 * remove debugger  
 * update readme with note about new mod_time addition  
 * more work on mod_time addition  
 * Add mod_time support  
 * Sort list of user/profiles by user name  
 * update CHANGELOG.md  

[1.7.5] ----- 2022-11-08
 * update project version  
 * improve hadnling of False boolean vs None value in dictionary cleaner  
 * update CHANGELOG.md  

[1.7.4] ----- 2022-11-07
 * update project version  
 * tweak README  
 * update CHANGELOG.md  

[1.7.3] ----- 2022-11-04
 * update project version  
 * add poetry back as make dependency  
 * update CHANGELOG.md  

[1.7.2] ----- 2022-11-04
 * update project version  
 * tweak do-install  
 * change installer to use bash array for app list (even tho we onlly have 1 here)  
 * tweak readme  
 * tidy  
 * update CHANGELOG.md  

[1.7.1] ----- 2022-10-31
 * update project version  
 * Change build from poetry/pip to python -m build/installer  
 * Add comment to PKGNBUILD about tomli not needed for python > 3.11  
 * update CHANGELOG.md  

[1.7.0] ----- 2022-10-31
 * update PKGBUILD version  
 * update CHANGELOG.md  
 * update project version  
 * sync PKGBUILD from aur  
 * update CHANGELOG.md  

[1.6.1] ----- 2022-10-30
 * update project version  
 * Update readme  
 * sync PKGBUILD from aur  
 * update CHANGELOG.md  

[1.6.0] ----- 2022-10-30
 * update project version  
 * -rpt now lists missing users/profiles from running server  
 * sync PKGBUILD from aur  
 * update CHANGELOG.md  

[1.5.0] ----- 2022-10-30
 * Add --details  
   Modifes -l, -rpt and -rrpt to provide detailed information in addition to the summary.  
 * update CHANGELOG.md  
 * update project version  
 * report: warn if server key out of date  
 * update CHANGELOG.md  

[1.4.0] ----- 2022-10-29
 * update project version  
 * report: handle cases where running server has old user key and other edge cases  
 * sync PKGBUILD from aur  
 * update CHANGELOG.md  

[1.3.2] ----- 2022-10-29
 * update project version  
 * update README  
 * -rrpt is boolean, no args needed  
 * add --run_show_rpt. Similar to --show_rpt, but runs wg-tool  
 * sync PKGBUILD from aur  
 * update CHANGELOG.md  

[1.3.1] ----- 2022-10-29
 * update project version  
 * bug fix: -inact user:prof made user inactive not just prof  
 * sync PKGBUILD with aur  
 * update CHANGELOG.md  

[1.3.0] ----- 2022-10-29
 * update project version  
 * Add new option --work_dir  
   Refactor and tidy code up some  
 * tweak readme  
 * sync PKGBUILD with aur  
 * tweak readme  

[1.2.3] ----- 2022-10-27
 * proj vers bump  
 * Add mising packages to PKGBUILD depends (thank you @figure on aur)  
 * upd changelog  

[1.2.2] ----- 2022-10-27
 * duh - turn off debugger .. sorry  
 * markdown newline fix  
 * word smith readme  

[1.2.1] ----- 2022-10-26
 * update project version  
 * tweak mardown format of readme  
 * update changelog  

[1.2.0] ----- 2022-10-26
 * new file show_rpt to support the --show_rpt option  
 * update changelog  
 * Adds support to parse output of wg show and provide user/profile names  
 * Add new/coming soon section to readme  
 * aur package now avail  
 * update changelog  

[1.1.1] ----- 2022-10-26
 * proj vers update  
 * update changelog  
 * installer: share archlinux into /usr/share/wg_tool  
 * update changelog  

[1.1.0] ----- 2022-10-26
 * key update fixes  
 * Dont mark server config changed when user configs changed  
 * bug fix with update server key  
 * duh  
 * bug fix with func name. Change mkdirs -> make_dir_path  

[1.0.2] ----- 2022-10-26
 * update changelog  
 * update vers 1.0.2  
 * tweak sample interface postup.nft  
 * update changelog  
 * word smithing contd  
 * word smithing  
 * update changelog  

[1.0.1] ----- 2022-10-25
 * prep for version 1.0.1  
 * update changelog  
 * tidy help a little  
 * update README  
 * update changelog  

[1.0.0] ----- 2022-10-25
 * Add --save_options which saves/restoreds --keep / --keep_wg history depth  

[0.9.2] ----- 2022-10-25
 * bug fix, we always created empty db/dated dir when not needed  
 * fixups, cleanups and fix bugs  
 * update changelog  

[0.9.1] ----- 2022-10-25
 * refactor and tidy code  
 * fix --clean_wg_configs to print default number keep  
 * update changelog  

[0.9.0] ----- 2022-10-24
 * update projec vers 0.9.0  
 * update project vers  
 * tweak options help  
 * Support for --active and --inactive to add / remove users:profile  
 * tidy up  
 * Add clean up support for db directories  
   -clc --clear_configs - clears configs/[server,users]db - we keep any references by links, keep 10 by default  
   -clw --clear_wg_configs clears wg-onfigs/[server,users]db - keep any link references, keep 4 by default  
   Add messaging support for verbose, error, warning - and yes support -v --verb as well.  
   Add more file_tools  
 * update changelog  
 * update to 0.2.0  
 * Add --verb option; by default less verbose  
 * Add archlinux PKGBUILD  
 * typo in install script  
 * add MIT license  
 * add changelog  

[0.1.0] ----- 2022-10-23
 * add initial readme draft  
 * add installer script for package builders  
 * Start a readme file  
 * Only update wg-config (server and users) if any changes  
 * rename user/config -> user/profiles  
 * tidy some code fragments  
 * library name change tools -> lib  
 * new files  
   toml - captures read/write for toml  
   import_user - first pass at user import tool  
   --import foo.conf bob:main  
   imports from foo.conf to user bob under config main  
 * Add scripts and pyproject  
 * second pass  
   - add import tool to import from wg user.conf  
   - change /users/xx.conf -> configs/users/xxx/xxx.conf  
   This allows us to clean up per user - without this any time based cleanup could easily remove some unchanged users entirely.  
   - various code improvements  
 * initial commit  

