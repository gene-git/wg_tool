.. SPDX-License-Identifier: MIT

#######
Contrib
#######

Ubuntu Notes
============

Provided by Jack Duan (@jduan00 via github #13)

I would like to share the steps I got it to work on Ubuntu 22.04. Feel free to include in your documentation to help others.


Install Prep
------------

Assume these are already installed.

.. code-block:: bash

    $ sudo apt install wireguard qrencode

Install necessary python3 packages for wg_tool:

.. code-block:: bash

    $ sudo apt install python3 python-is-python3 python3-poetry python3-build \
    python3-installer python3-qrcode python3-tomli-w python3-tomli python3-netaddr

Build and install
-----------------

.. code-block:: bash

    $ git clone https://github.com/gene-git/wg_tool
    $ cd wg_tool

    $ sudo pip install hatchling

    $ /usr/bin/python -m build --wheel --no-isolation

    $ sudo ./scripts/do-install /

Getting wg and wg-tool to work
------------------------------

.. code-block:: bash

    $ sudo -i
    # cd /etc/wireguard

    # wg-tool --init

    # vi config/server/server.conf

Add the first set of users with wg-tool

.. code-block:: bash

    # wg-tool --add_user --dns_search Mary:mac,iphone,ipad

    # ln -s wg-configs/server/wg0.conf .

    # systemctl enable wg-quick@wg0
    # systemctl start wg-quick@wg0
    # systemctl status wg-quick@wg0

    # wg show

Add more users

.. code-block:: bash

    # cd /etc/wireguard
    # wg-tool --add_user --dns_search Joe:mac,iphone,ipad
    
    # systemctl reload wg-quick@wg0

    # wg show

    # wg-tool --list_users

    # wg-tool -rrpt

iptables
--------

Also, I don't use PostUp scripts since persistent iptable rules are used.

.. code-block:: bash

    # apt install iptables-persistent
    # systemctl status iptables
    # systemctl enable iptables
    # systemctl restart iptables

Change /etc/iptables/rules.v4
Note

 * 192.168.100.0/24 is used for wg subnet.
 * On Ubuntu ens3 is the default network device name

.. code-block:: 

    # == For Wireguard VPN ==
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    # -- NAT for vpn clients from wireguard
    -A POSTROUTING -o ens3 -s 192.168.100.0/24 -j MASQUERADE
    COMMIT
    # ---------------------
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A INPUT -i lo   -j ACCEPT
    -A INPUT -i wg+  -j ACCEPT
    -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A INPUT -m state --state INVALID             -j DROP
    # -- Wireguard ports
    -A INPUT -i ens3 -p  udp -m multiport --dports 51820 -m state --state NEW -m limit --limit 10/sec --limit-burst 20 -j ACCEPT
    -A INPUT -i ens3 -p icmp -m icmp --icmp-type 8 -m limit --limit 5/sec -j ACCEPT
    # -- last as the default rule for input
    -A INPUT -j DROP
    # -- forward --
    -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A FORWARD -m state --state INVALID             -j DROP
    -A FORWARD -i wg+  -s 192.168.100.0/24          -j ACCEPT
    -A FORWARD -j REJECT --reject-with icmp-port-unreachable
    # -- out --
    -A OUTPUT -m state --state INVALID -j DROP
    COMMIT
    # == EOF ==


Run commands:

.. code-block:: bash

    # systemctl restart iptables

    # iptables -nvL
    # iptables -t nat -nvL

