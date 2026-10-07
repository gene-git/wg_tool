********
Appendix
********

MTU Observation
===============

I came across one hotel wifi where the vpn worked providing internet access, but using
ssh was problematic.

.. code-block:: bash

    ssh -v internal-host

would hang right after it logged::

    expecting SSH2_MSG_KEX_ECDH_REPLY

The *fix/work around* was changing the MTU setting from 1500 down to 1400 on my laptop
while at that hotel.

With that change everything worked normally again.

I have only ever had to modify the MTU at this one location, but I mention it in case
someone else has a similar issue.



.. _Install:

Install
=======

While it is simplest to install from a package manager, manual 
installs are done as folllow:

First clone the repo :

.. code-block:: bash

   git clone https://github.com/gene-git/wg_tool

Then install to local directory.
When running as non-root then set root_dest to a user writable directory.

.. code:: bash

    rm -f dist/*
    /usr/bin/uv build --wheel --no-build-isolation
    root_dest="/"
    ./scripts/do-install $root_dest

Dependencies
------------

**Run Time** :

  * python  (3.14+)
  * python-cryptography
  * py-cidr 
  * python-qrcode
  * wireguard-tools
  * nftables
  * tomli_w

**Building Package**:

  * git
  * meson
  * meson-python
  * rsync

License
========

Created by Gene C. and licensed under the terms of the GPL-2.0-or-later license.

 * SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>

.. _py-cidr: https://github.com/gene-git/py-cidr
.. _py-cidr AUR: https://aur.archlinux.org/packages/py-cidr
.. _wireguard: https://www.wireguard.com
