.. SPDX-License-Identifier: GPL-2.0-or-later

Recent Changes
==============

**10.5.0**

* Add missing checkdepends() to PKGBUILD

**10.4.0**

* Fix goofy typo in Arch PKGBUILD

**10.3.0**

* Change Arch package dependencies that have been renamed:

  - pyconcurrent -> python-pyconcurrent

* Add check() to PKGBUILD

**10.1.0**

* linux client config output now uses tools provided by *wg-client*.

  If you are using linux clients please install *wg-client* package. 
  It is much better than what was provied in earlier version of wg_tool.
  
  wg-client provides resolv-manager along with post-up.sh and post-dn.sh.
  These replace the wg-post-updn script which has therefore been dropped.

  wg_tool now also produces wireguard-resolv.conf file since the 
  new post-up.sh / post-dn.sh scripts from wg-client require a resolv.conf file
  to use while wireguard is running. 

  To get the updated configs and the resolv file use: 

    wg-tool --refresh

* Add wg-client to the optional packages in PKGBUILD.
* Package management is now done by meson/mesonpy (drop uv and pyproject.toml)

* Disable color for --help as it looks bad on dark terminals.


**10.0.0**

* Migrate to PyCidr from Cidr module.
  
  Lots of network code simplication and it runs faster as well.
  This does add tow new package dependencies coming from new *py-cidr* package: 
  
  * `cidrtools <https://github.com/gene-git/cidrtools>`_ and `AUR <https://aur.archlinux.org/packages/cidrtools>`_
  * `cidrtools-cffi <https://github.com/gene-git/cidrtools-cffi>` and `AUR <https://aur.archlinux.org/packages/cidrtools-cffi>`_

* Drop unused files
* Switch to meson/uv for package building
* Move examples to src/tests and add test runner to confirm the output 
  wireguard configs match a baseline set.

**9.2.2**

* Code Reorg
* Switch packaging from hatch to uv
* Testing to confirm all working correctly on python 3.14.2
* 3.14 argparse introdiced color - it can be turned of with env PYTHON_COLORS=0.
  The colors are not currently adjustable - is improved in python 3.15.
