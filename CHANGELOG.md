# Changelog

## [3.2.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-11-28
 - typo  
 - update CHANGELOG.md  

## [3.1.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-11-28
 - fix typo creating new user profile with -dnssrc/-dnslin  
 - tweak readme  
 - update CHANGELOG.md  

## [3.0.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-11-28
 - Adds 3 new options:  
   - --mod_users : modify existing user profile (with --dns_search and --dns_linux)  
   - --dns_search : adds support for dns search domain list  
   - --dns_linux : adds support for managing resolv.conf instead of relying on qg-quick/resolconf  
 - update CHANGELOG.md  

## [2.1.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-11-24
 - - improve error msg  
   - Check conf before using it - added when auto updating older configs using mtime of config  
   - minor tweak to bash variable check in install script  
 - update CHANGELOG.md  

## [2.0.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-11-11
 - list users report now sorts by user name  
   Add support for tracking config modification date-time. mod_time displayed in list user report  
 - update CHANGELOG.md  

## [1.7.5] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-11-08
 - Improve handling of booelan False vs None in pre-file-write dictionary cleaner  
 - update CHANGELOG.md  

## [1.7.4] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-11-07
 - tweak readme  
 - update CHANGELOG.md  

## [1.7.3] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-11-04
 - add poetry back to PKGBUILD makedepends  
 - update CHANGELOG.md  

## [1.7.2] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-11-04
 - change installer to use bash array for app list (even tho we onlly have 1 here)  
   tweak readme  
 - update CHANGELOG.md  

## [1.7.1] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-31
 - Change build from poetry/pip to python -m build/installer  
 - update CHANGELOG.md  

## [1.7.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-31
 - Add support for python 3.11 tomllib  
 - update CHANGELOG.md  

## [1.6.1] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-30
 - update readme  
 - update CHANGELOG.md  

## [1.6.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-30
 - -rpt now lists missing users/profiles from running server  
 - update CHANGELOG.md  

## [1.5.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-30
 - Add --details  
   Modifes -l, -rpt and -rrpt to provide detailed information in addition to the summary.  
 - update CHANGELOG.md  

## [1.4.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-29
 - report: handle cases where running server has old user key and other edge cases  
 - update CHANGELOG.md  

## [1.3.2] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-29
 - add --run_show_rpt. Similar to --show_rpt, but runs wg-tool  
 - update CHANGELOG.md  

## [1.3.1] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-29
 - bug fix: -inact user:prof made user inactive not just prof  
 - update CHANGELOG.md  

## [1.3.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-29
 - Add new option --work_dir  
   Refactor and tidy code up some  
 - upd changelog  
 - tweak readme  
 - tweak readme and sync PKGBUILD  
 - upd changelog  

## [1.2.3] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-27
 - Add mising packages to PKGBUILD depends (thank you @figue on aur)  
 - upd changelog  

## [1.2.2] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-27
 - duh - turn off debugger .. sorry  
 - markdown newline fix  
 - word smith readme  
 - update changelog  

## [1.2.1] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-26
 - update project vers  
 - actually add the code to make wg_show report :)  

## [1.2.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-26
 - Adds support to parse output of wg show and provide user/profile names  
 - Add new/coming soon section to readme  
 - readme - aur package now avail  
 - update changelog  

## [1.1.1] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2022-10-26
 - proj vers update  
 - installer: share archlinux into /usr/share/wg_tool  
 - Ready to share  

