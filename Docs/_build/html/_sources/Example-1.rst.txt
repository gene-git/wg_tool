.. SPDX-License-Identifier: GPL-2.0-or-later

.. _Example_1:

Working Example 1
-----------------

This example has a single wireguard gateway, *wg-A*, providing access to Office-A 
internal LAN, *192.168.1.0/24* to it's clients. It also offers internet access for 
any clients wanting all internet traffic to go through the vpn.

This expands on the rather :ref:`Simple-example` shown earlier.

As we do in all the examples, we first walk through 
:ref:`Example-1-tool`. 

At the end of the walk throgh, we show the resulting :ref:`Example-1-standard` that are created.
In this example the result will be the gateway and it's client configs.
Client configs come with a QR code carrying the same information.

These configs are the ones consumed by wireguard itself. 


Network Diagram
+++++++++++++++

.. image:: ./diagrams/Example-1.png
   :alt: Example 1 
   :scale: 50 %
   :align: center


We find it helpful to make a small table with the goals for this vpn.

The table lists each of the peers and what they want from or offer to other peers.

Gateways are those peers which other connect to.
All gateways are marked.  Some gateways may provide internet access. 

Some peers may offer network access to specific networks.

Some clients may want their internet traffic to flow through the vpn while
others may want to access the internet directly and use the vpn soley to
access internal networks.

For all examples we use a vpn named *vpn-test*.

.. include:: ./latex-includes/latex-format.rst

Goals Table
+++++++++++

.. list-table:: Example 1 Goals 
   :header-rows: 2

   * - 
     - 
     - 
     - Internet 
     - 
     - Networks 
     - 
   * - Account
     - Profile
     - Gateway
     - wanted
     - offered
     - offered
     - wanted
   * - servers
     - wg-A
     - |ctron| ✓ |ctroff| 
     - |ctron| ✗ |ctroff|
     - |ctron| ✓ |ctroff| 
     - 192.168.1.0/24
     - \-
   * - user-1
     - laptop
     - |ctron| ✗ |ctroff|
     - |ctron| ✓ |ctroff| 
     - |ctron| ✗ |ctroff|
     - \-
     - 192.168.1.0/24
   * - user-2
     - laptop
     - |ctron| ✗ |ctroff|
     - |ctron| ✓ |ctroff|
     - |ctron| ✗ |ctroff|
     - \-
     - 192.168.1.0/24
   * - user-3
     - laptop
     - |ctron| ✗ |ctroff|
     - |ctron| ✗ |ctroff|
     - |ctron| ✗ |ctroff|
     - \-
     - 192.168.1.32/28

*wg-A* also offers internet access to it's peers. Some peers, such as *user-3.laptop*
may prefer to access the internet directly and only use *wg-A* to access *LAN-A*. 

*user-3.laptop* is using *split routing* (also called *split tunnelling*),
since it routes *LAN-A* traffic over the VPN, while all other traffic goes direct. 

*user-1.laptop*, on the other hand has all of it's network traffic go 
via *wg-A*.

In this example we use the following networks:

* *vpn.example.com:51820* : Endpoint of gateway *wg-A*
* *10.77.77.0/24* : vpn internal network. 
* *192.168.1.0/24* : *LAN-A* the internal Office A LAN.

.. _Example-1-tool:

Generating the Wireguard Configs Using wg-tool
++++++++++++++++++++++++++++++++++++++++++++++

This is a step by step walk through using the tool to create the configs
that wireguard uses. Once done you can browse the configs that result.

Please never edit any files in Data/. To make a change,
or to view the editable variables, use *wg-tool --edit <ID>*.

That saves a file in the Edits/ directory which you can edit
and, if you so choose, merge any changes back with *wg-tool --merge <file>*.

To create your own example, work in an empty directory of your choosing.
First create a "vpn" group hich we'll label *vpn-test* here. This contains
all related wireguard peers. A peer can be a gateway or a client.

Each peer is is denoted by an identifier which takes the form:

.. code-block:: text

    <vpn name>.<account name>.<profile name>

Names are alphanumeric, with some restrictions on special characters [#valid_names]_. 
For example periods are not allowed (for obvious reasons). 

We find it convenient to use *servers* for 
the *account name* for things that run on a server, like gateways.
User names make a good account name choice for people. 

There are some instances where an ID may be shortened. For example to
create a new vpn, we can drop account and/or profile part.
Later we use the full ID to create gateway and client profiles.

Make Working Directory
^^^^^^^^^^^^^^^^^^^^^^

The first step is to establish a working directory:

.. code-block:: bash

    mkdir my-examples
    cd my-examples
    wg-tool -wkd ./

Note that networks in the *AllowedIPs* wireguard config
are compacted to their minimal CIDR representation. The pre-compacted
list, perhaps most useful during testing, is provded as a comment in the config file. 
For additional information please see :ref:`Compacting`. 

Make New VPN called vpn-test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We now create a new vpn named *vpn-test*. For this the ID is simply *vpn-test*:

.. code-block:: bash

    wg-tool -new vpn-test

This also invokes the *edit* option and displays the file name.
This file will be ./Edits/vpn-test-info.mods.

Please edit this file and add any relevant VPN information.
In our case we really may only need to add a DNS server (or 2), host or IP.

.. code-block:: none

   dns = ['10.10.10.10']
   peer_to_peer = false

Note that elements in *dns* are dns servers. They can be an IP address
or a hostname; hostnames will be converted to their IP address
using local dns resolver.

For more information about DNS please see :ref:`dns-note`.

You can change the internal tunnel network(s) if you prefer or leave 
the default setting. 

Leave the peer_to_peer set to *false* unless you 
want peers to communicate directly with one another, rather than just
with the gateway(s).

The effect of turning on peer to peer is to change
the wireguard *AllowedIPs* variable to 
permit the entire vpn network (*/24 or */64* for IPv6) 
instead of a single IP address for every peer.

Leave it to *false* to match the example configs at the 
given at the end. This is the typical setting.

Never modify the *tag* field - it is a unique identifier used to 
ensure any edits go to the correct place.

Next merge any changes:

.. code-block:: bash

   wg-tool --merge Edits/vpn-test-info.mods

You can make changes at any time using the *--edit* option 
which saves a then current version to the file.

You can change this at any time using *wg-tool --edit vpn-test*, 
modify the setting and *-merge* the changes back.

Add Gatewway wg-A
^^^^^^^^^^^^^^^^^

Next we add the gateway and some clients. The tool handles all keys and 
internal vpn IP addresses.

We'll use an *account* called *servers* with one gateway profile, *wg-A*.

So now do:

.. code-block:: bash

   wg-tool --new vpn-test.servers.wg-A
   wg-tool --edit vpn-test.servers.wg-A

Edit the file, filename is displayed. In this case
it will be *Edits/vpn-test.servers.wg-A.mods*.

Since every gateway must be reachable, an *Endpoint* is required.
We also want to provide access to Office A's internal LAN. 

*wg-A* has access to an internal network which we will 
allow it to share with other peers. We do this by
setting the *internet_offered* with the network. This
can be a list of networks, but we are only providing
access to one.

This means we need to modify a few lines as shown:

.. code-block:: none

   Endpoint = "vpn_A.example.com:51820"
   internet_offered = true
   internet_wanted = false
   nets_offered = ["192.168.1.0/24"]
   post_up = ['/usr/bin/nft -f /etc/wireguard/scripts/postup.nft']
   post_down = ['/usr/bin/nft flush ruleset']

The *post_up/down* are scripts wireguard runs bringing vpn tunnel up/down.
The nftables rules allow traffic to be NAT'd to and from the tunnel.
If you wish, you can add another DNS server here as well (dns=..).

As we did with vpn edits, merge these changes back using:

.. code-block:: bash

    wg-tool --merge Edits/vpn-test.servers.wg-A.mods

At this point there will be a wireguard config for *wg-A* in

.. code-block:: none

   Data-wg/vpn-test/servers/wg-A.conf

It will have an *Interface* section but no peers, since we haven't yet created
anything else beside the one gateway.


Add 3 Clients Peers
^^^^^^^^^^^^^^^^^^^

Now we're ready to add some client profiles. 

We create 3 users where eech user has one profile named *laptop*. 
We choose *user-1*, *user-2* and *user-3* for the 3 account names. 

.. code-block:: bash

   wg-tool -new vpn-test.user-1.laptop vpn-test.user-2.laptop vpn-test.user-3.laptop


Making LAN Network Available to Clients
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Split Routing
^^^^^^^^^^^^^

Lets also make user-3.latpop use split routing

By default the laptop clients route all their traffic via the gateway - both 
for LAN as well as internet traffic.

Lets edit *vpn-test.client-3:laptop* to change it to split rouing..
This means LAN traffic will be routed via the vpn and all 
regular internet traffic is routed directly. 

As usual edit the ID:

.. code-block:: bash

   wg-tool --edit vpn-test.user-3.laptop

and modify the file ./Edits/vpn-test.user-3.laptop.mods:

.. code-block:: none

   internet_wanted = false

Then merge the change back. The *edit* option always prints the filename to be edited and merged:

.. code-block:: bash

   wg-tool --merge Edits/vpn-test.user-3.laptop.mods

Network Access
^^^^^^^^^^^^^^

*wg-A* is offering to share its' LAN, *192.168.1.0/24*. We now
confgure each of the user laptop configs to request
access to it. 

We could use *--edit* for each of the IDs to accomplish this.
Here we would set the variable *nets_wanted = ["192.168.1.0/24"]* 
for each and then use *--merge* again.

Alternatively, we can use a command line option, which for this
change is a little easier to do.

Lets use the command line option 
to assign network access for each of the clients.

We will permission user-1.laptop and user-2.laptop with
access to *192.168.1.0/24*.

And, for fun, we limit user-3.laptop to the subnet *19.168.1.32/28*

.. code-block:: bash

   wg-tool --nets-wanted-add "192.168.1.0/24" vpn-test.user-1.laptop vpn-test.user-2.laptop
   wg-tool --nets-wanted-add "192.168.1.32/28" vpn-test.user-3.laptop


We're done.

Listing What We Have
^^^^^^^^^^^^^^^^^^^^

We can show everything looks good by using *--list* (or *-l*) option.

You can add *-v* or *-vv* to get more verbose output.
Using *-lv* will also show networks while *-lvv* will show public keys
and any *hidden* items. You can also filter what is shown by 
<vpn>.<account> to show all profiles or <vpn>.<account>.<profile>

For example, 

.. code-block:: bash
    
    wg-tool -lv

And the output should look similar to this:

.. code-block:: text

   Loading vpn-test
    ✓ vpn-test         250914-202654:

        ✓ servers      250914-202654:
                         ✓ wg-A                 250914-202702 (gateway)
                                 nets_offered : ['192.168.1.0/24', 'internet']

        ✓ user-1       250914-202655:
                         ✓ laptop               250914-202702
                                  nets_wanted : ['192.168.1.0/24', 'internet']

        ✓ user-2       250914-202655:
                         ✓ laptop               250914-202702
                                  nets_wanted : ['192.168.1.0/24', 'internet']

        ✓ user-3       250914-202655:
                         ✓ laptop               250914-202702
                                  nets_wanted : ['192.168.1.32/28']


The date/times are the last modification time.
The terminal output may show some ascii colors.

All being well, this will show 1 vpn (*vpn-test*) with 1 gateway under servers.wg-A.
It should also show 3 users each with a laptop profile. 

Wireguard Config Files
^^^^^^^^^^^^^^^^^^^^^^

The standard wireguard config files are all saved under the *Data-wg* directory.

In our case the configs files are under *Data-wg/vpn-test/*.
The config for the *wg-A* gateway will be in:

.. code-block:: none

   Data-wg/vpn-test/servers/wg-A.conf

while client-1 will be under

.. code-block:: none

   Data-wg/vpn-test/user-1/laptop.conf
    
and similarly for the other 2 clients.

All being well, these wireguard config files will match those we showed at in the next section.

Configs as QR Code
^^^^^^^^^^^^^^^^^^

For non-gatways, a QR code version of the same config is generated under each 
account's *qr* directory. For example:

.. code-block:: none

   cat Data-wg/vpn-test/user-1/laptop.conf
   Data-wg/vpn-test/user-1/qr/laptop.png

You will also see that every pair of peers has it's own unique pre-shared key. 
This is used for all communications between those peers and
adds additional security against post-quantum attacks.

The PSK shared between a gateway and a client will be in the gateway config
in the *Peer* section for the client and the same key will be in the
client config in the *Peer* section for that gateway.

These all have both IPv4 as well as IPv6 tunnel addresses automatically generated. We
skipped when listing the configs at the begining of this example.

Wireguard client apps usually can take either the text *.conf* file or use a 
camera to read the QR code.
The QR code has exactly the same information as the corresponding *.conf* file.

You can view the QR image and see the content of a QR code using, for example [#zbar]_:

.. code-block:: bash

   zbarimg --raw Data-wg/vpn-test/user-1/qr/laptop.png

This displays the same data as the config, without any comments which we 
stripped out before building the QR code.


.. _Example-1-standard:

Standard Wireguard Configs
++++++++++++++++++++++++++

Taken from *Data-wg/...*.

Note that leading whitespace should not be used in actual config files.
In this document we added extra white space to the output configs solely 
to aid in visually separating the sections from one another.

**wg-A**

* cat Data-wg/vpn-test/servers/wg-A.conf

.. code-block:: none


    [Interface]          # servers wg-A (gateway)
        PrivateKey           = <privkey>
        ListenPort           = 51820
        Address              = 10.77.77.1/24, fc00:77:77::1/64
        PostUp               = /usr/bin/nft -f /etc/wireguard/scripts/postup.nft
        PostDown             = /usr/bin/nft flush ruleset


    #
    # Clients
    #

    [Peer]               # user-1 laptop
        PublicKey            = <pubkey user-1.laptop>
        PresharedKey         = <psk wg-A x user-1.laptop>
        AllowedIPs           = 10.77.77.2/32, 192.168.1.0/24, fc00:77:77::2/128

    [Peer]               # user-2 laptop
        PublicKey            = <pubkey user-2.laptop>
        PresharedKey         = <psk wg-A x user-2.laptop>
        AllowedIPs           = 10.77.77.3/32, 192.168.1.0/24, fc00:77:77::3/128

    [Peer]               # user-3 laptop
        PublicKey            = <pubkey user-3.laptop>
        PresharedKey         = <psk wg-A x user-3.laptop>
        AllowedIPs           = 10.77.77.4/32, 192.168.1.32/28, fc00:77:77::4/128

**user-1**

* cat Data-wg/vpn-test/user-1/laptop.conf

.. code-block:: text


    [Interface]          # user-1 laptop  
        PrivateKey           = <privkey>
        Address              = 10.77.77.2/32, fc00:77:77::2/128
        DNS                  = 10.10.10.10

    #
    # Gateways
    #

    [Peer]               # servers wg-A (gateway) 
        PublicKey            = <pubkey wg-A>
        PresharedKey         = <psk wg-A x user-1.laptop>
        # pre-compacted        0.0.0.0/0, 10.77.77.1/32, 192.168.1.0/24
        # pre-compacted        ::/0, fc00:77:77::1/128
        AllowedIPs           = 0.0.0.0/0, ::/0
        Endpoint             = vpn_A.example.com:51820


**user-2**

* cat Data-wg/vpn-test/user-2/laptop.conf

.. code-block:: none
   
    [Interface]          # user-2 laptop  
        PrivateKey           = <privkey>
        Address              = 10.77.77.3/32, fc00:77:77::3/128
        DNS                  = 10.10.10.10

    #
    # Gateways
    #

    [Peer]               # servers wg-A (gateway) 
        PublicKey            = <pubkey wg-A>
        PresharedKey         = <psk wg-A x user-2.laptop>
        # pre-compacted        0.0.0.0/0, 10.77.77.1/32, 192.168.1.0/24
        # pre-compacted        ::/0, fc00:77:77::1/128
        AllowedIPs           = 0.0.0.0/0, ::/0
        Endpoint             = vpn_A.example.com:51820

**user-3**

* cat Data-wg/vpn-test/user-3/laptop.conf
* using split routing

.. code-block:: none

    [Interface]          # user-3 laptop  
        PrivateKey           = <privkey>
        Address              = 10.77.77.4/32, fc00:77:77::4/128
        DNS                  = 10.10.10.10

    #
    # Gateways
    #

    [Peer]               # servers wg-A (gateway) 
        PublicKey            = <pubkey wg-A>
        PresharedKey         = <psk wg-A x user-3.laptop>
        AllowedIPs           = 10.77.77.1/32, 192.168.1.32/28, fc00:77:77::1/128
        Endpoint             = vpn_A.example.com:51820


.. rubric:: Footnotes

.. [#valid_names] Valid names comprise letters, numbers and = - _  ~ + ; : @
.. [#zbar] zbarimg provided by the *zbar* package.
.. [#rfc3442] https://datatracker.ietf.org/doc/html/rfc3442


.. include:: ./Example-2.rst
