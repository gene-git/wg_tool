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

  * python (3.13 or later)
  * python-cryptography
  * py-cidr 
  * python-qrcode
  * wireguard-tools
  * nftables (for wireguard server postup.nft)
  * tomli_w (aka python-tomli_w )

**Building Package**:

  * git
  * uv
  * uv-build (aka python-uv-build)
  * sphinx
  * myst-parser
  * texlive-latexextra  (texlive tools, this is archlinux package)
  * rsync


Documentation
-------------

The documentation is available in *src/data/docs/wg-tool.pdf* as well
an html version *src/data/docs/html*.

The source is also available to build your own:

.. code-block:: bash

   ./build-manual.sh

This does need sphinx (see :ref:`Install`)


Philosophy
----------

While we follow PEP-8, PEP-257, PEP-484 and PEP-561, we prefer to allow 
max line length of 100 rather than 79 in some situations.

We follow the *live at head commit* philosophy as recommended by 
Google's Abseil team [1]_.  This means we recommend using the
latest commit on git master branch. 


License
========

Created by Gene C. and licensed under the terms of the GPL-2.0-or-later license.

 * SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>

.. _Github: https://github.com/gene-git/wg_tool
.. _Archlinux AUR: https://aur.archlinux.org/packages/wg_tool
.. _wg-client: https://github.com/gene-git/wg-client
.. _py-cidr: https://github.com/gene-git/py-cidr
.. _py-cidr AUR: https://aur.archlinux.org/packages/py-cidr
.. _wireguard: https://www.wireguard.com

.. [1] https://abseil.io/about/philosophy#upgrade-support

