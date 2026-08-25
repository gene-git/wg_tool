.. SPDX-License-Identifier: GPL-2.0-or-later

Recent Changes
==============

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
