.. SPDX-License-Identifier: GPL-2.0-or-later

.. _Example_4:

.. rst-class:: centered-table-text

Working Example 4
=================

This example introduces the usage of IP groups.
Here we add a new peer, *vpn1.customers.abc_corp* together
with an *admin* ip group. *abc_corp* will allow access to members of the
admin group. Sally will get *admin* membership.


We will first enlarge the vpn network(s) to make it a little simpler
to make subnets for admin ip group. We will then create the *admin* group
and make sally a member. The last change is to adit *abc-corp* 
and have it permit *admin* group access.

As we did previoously, we will continue to add the the previous examples.
This example closely follows the section :ref:`Ip_Groups`.

The example script *create-example-4* runs through the complete example if you 
want to quickly see the end result.

Expand the VPN networks
-----------------------

Lets expand the networks a bit:

.. code-block:: bash

   wg-tool --edit vpn-test

Now edit the file
Edit the file as before, (*Edits/vpn-test-info.mods*).

Change the network settings as shown here:

.. code-block:: none

   networks:
   - 10.77.76.0/22
   - fc00:77:77::/56

Then merge changes back:

.. code-block:: none

   wg-tool --merge Edits/vpn-test-info.mods


Add IP Group
------------

We now define an *admin* ip group comprised of subnets of the above vpn networks:

.. code-block:: bash

   wg-tool --add-ip-grop admin "10.77.79.224/27,fc00:77:77:fe::/64" --ident vpn-test

Since *vpn-test* uses both IPv4 and IPv6, we provide subnets of both.


Put user-1.laptop into admin Group
----------------------------------

.. code-block:: bash

   wg-tool --ip-group admin vpn-test.user-1.laptop


Add ABC-Corp Peer
-----------------

Here we create a new account *customers* along with a new peer *abc-corp* which
allows access to members of the *admin* ip group.

.. code-block:: bash

    wg-tool --new vpn-test.customers.abc-corp
    wg-tool --allow-ip-groups admin vpn-test.customers.abc-corp


All done. Lets review some of the resulting wireguard configs

.. _Example-4-standard:

Standard Wireguard Configs
--------------------------

Let's focus on those peers impacted by the *admin* ip group.
Namely the peer *vpn1.users.sally* along with *vpn1.customers.abc-corp*.

**user-1.laptop**

Only change is here is that the IP Addresses, both IPv4 and IPv6, are drawn fromt the *admin* 
ip group subnets:

.. code-block:: none

    10.77.79.224/27 and fc00:77:77:fe::/64

.. code-block:: none

   [Interface]          # user-1 laptop
   PrivateKey           = oJHyiAoMTvTkXpXvfkm+LZEFP4jS5UZ7xfRGywjIf20=
   Address              = 10.77.79.226/32, fc00:77:77:fe::2/128
   DNS                  = 10.10.10.10

   #
   # Gateways
   #

   [Peer]               # servers wg-A (gateway)
   PublicKey            = 4KSBbV3MFNeKv6uA5l1O5TiU/5a3s1w9bmU2waPZVj0=
   PresharedKey         = /64sqfimz+H4Ik+qKkIEqpFSHizdd2KPxQwzlWhGjAU=
   # pre-compacted        0.0.0.0/0, 10.77.77.1/32, 192.168.1.0/24
   # pre-compacted        ::/0, fc00:77:77::1/128
   AllowedIPs           = 0.0.0.0/0, ::/0
   Endpoint             = vpn_A.example.com:51820



**ABC-corp**

As you can see, the AllowedIPs are for gateway and ips belonging to
the *admin* ip group.

.. code-block:: none 


   [Interface]          # customers abc-corp
   PrivateKey           = mOcDcBoLmtFSt/Vh/eqcJg63OjWbD9i0TTToHRo/u0A=
   Address              = 10.77.76.1/32, fc00:77:77::2/128
   DNS                  = 10.10.10.10

   #
   # Gateways
   #

   [Peer]               # servers wg-A (gateway)
   PublicKey            = 4KSBbV3MFNeKv6uA5l1O5TiU/5a3s1w9bmU2waPZVj0=
   PresharedKey         = qjGlCniGGMkpyd76Keyx1GTXONdVJTXiyxQrUkfbQBA=
   AllowedIPs           = 10.77.77.1/32, 10.77.79.224/27, fc00:77:77::1/128
   AllowedIPs           = fc00:77:77:fe::/64
   Endpoint             = vpn_A.example.com:51820

