.. SPDX-License-Identifier: GPL-2.0-or-later

*******
wg-tool
*******

Overview
========

`Wireguard <https://www.wireguard.com>`_ is a superb vpn built in to the linux kernel.
It is robust and super fast.
While the majority of wireguard servers run on linux, they are found on other
operating systems as well. Most platforms, from desktops to mobile phones, 
have wireguard clients available. We found wireguard to be more robust
and faster than many legacy types of vpns.

A wireguard network is a collection of *peers* that are able to securely
communicate with one another. Some peers, known as gateways, allow other peers
to connect to them. Peers that are not gateways are called clients.

A basic vpn has a wireguard gateway and several clients that can use the gateway. 
The gateway may provide access to internel networks.
It may also allow clients to have all their internet traffic flow via the gateway.

Since traffic between the client and the gateway is encrypted, this provides
privacy and security. Wireguard crypto mechanisms include pre-shared keys
(*PSKs*) that provide additional resistance against post quantum attacks.
For maximum security a *PSK* should be unique to each pair of peers that
communicate with one another.

*wg-tool* is a wireguard configuration tool that 
simplifies managing all aspects of wireguard vpn setups.

It handles multiple gateways (e.g. office locations), sharing
of internal networks as well as split tunneling (internet via vpn or not).

It guarantees that all gateway and client configs remain
consistent with one another. Two peers that communicate with one another use
encryption and therefore they share key information. By consistent we  
mean that both of those peers always use the same public and pre-shared keys.

While *PSKs* are not mandatory in wireguard, they do enhance security.
There can be many pairs of *peers* with each pair sharing a unique *PSK*. 
*wg-tool* quietly takes care of all of them for you.

Wireguard gateway reports (created by running *wg show*) identify peers by their public key.
The tool can display these reports using their corresponding user friendly names. 
Solving a long standing, if minor, *annoyance*.

We built *wg-tool* to make our own VPN administration simple and robust. 

Where to Get wg-tool
--------------------

Available at:

* :Github:`wg_tool`
* :AUR:`wg_tool`

On Archlinux it can be installed from the AUR or using the 
PKGBUILD provided in packaging directory.

All git tags are signed with an arch@sapience.com key available via WKD
or from the `sapience.com <https://www.sapience.com/tech>`_ website. Add the key to your package builder gpg keyring.
The key is included in the Arch package and the source= line with *?signed* at the end can be used
to verify the git tag. You can also manually verify the signature as usual with 
*git tag -v <tag>*.

For those with linux road warriers, there is a :Github:`wg-client` companion package. 
This is a linux client command line tool packaged with a graphical 
program that makes it very simple to start and stop a wireguard client for any user.

We offer three working examples. In each example the goals are explained
followed by a walk through using *wg-tool*. The resulting standard wireguard configs 
are then provided .

See :ref:`Examples` section. 

Documentation source along with pre-generated PDF and html versions 
are in the *Docs* directory. All documentation is written using restructured text.

Key features
============

* Simplifies wireguard administration.
* Guarantees gateway and peer configs remain synchronized (public/preshared keys).
* Handles key generation and updates.
* Each *account* can have multiple profiles (vpn1.alice.laptop vpn1.alice.phone etc.)
* Accounts and/or profiles can be marked (in)active.
* Wireguard's standard 'wg show'report has public keys transformed into 
  user friendly acccount.profile names.

  This feature solves a long standing wireguard annoyance in a simple way 
  by showing names instead of public keys output by *wg show*.
  Also provides check on server config status being current and if it needs to be
  restarted with new config.

* Supports importing from existing wireguard config files.

New / Interesting
=================

** 8.2.0**

* Command line option completion optionally available. 

  See :ref:`Completion` section in the manual for details how to use this.

**Major Version 8.0.0**

* Re-write pretty much from scratch. New design and fresh start.
* Modern coding standards: PEP-8, PEP-257 and PEP-484 style and type annotations
* Can now manage multiple VPN's
* Each VPN has a number of *accounts* and each account may have multiple profiles.
  Some profiles may be gateways (can be connected to) while others are clients
  (connect to one or more gateways).
* Support more use cases than earlier versions.
* Provide walk through :ref:`Examples` for 3 common use cases
* The enhancements require significant data format changes. 

  To make the upgrade as simple and easy as possble,
  existing data from earlier versions can be auto migrated to 
  the new format with the *-migrate* option.

  Please see :ref:`migrating` for more details.

* Network manipulations are now built on the *py-cidr* module.
  Available at :Github:`py-cidr` and :AUR:`py-cidr AUR`.

* New way to modify profiles. 
  
  The *--edit* option creates a text file. The file 
  uses standard TOML (key = value) format. Simply edit the file and then 
  use the *--merge* option to incorporate those changes.

  This is simple and clean and makes it easy to modify whatever may be needed
  in one quick edit and merge.

  There are still many command line options which can be particularly helpful
  making bulk changes. 

* Improved command line help. 
  
  Command line option help is now organized by category:

.. code-block:: text

    migrate, edit/merge, reporting, general and stored options.

See *wg-tool --help* for more info or :ref:`Options-section`.

* Document most features including migration, importing, and
  making modifications.

*************
Documentation
*************

PDF and HTML
============

The complete documentation is available in *Docs/wg_tool.pdf* as well
an html version - just point a browser at *Docs/html*.

The document source is also available to build your own:

.. code-block:: bash

   make latexpdf; make latexpdf
   make html

This requires some sphinx packages being available (see :ref:`Install`)

***************
Getting Started
***************

Brief Wireguard Background
==========================

It may be useful to review the wireguard documentation https://www.wireguard.com/.
The key section on *Cryptokey Routing* describes how peers communicate securely with 
one another. In addition, the man pages for *wg-quick* and *wg* offer a lot of useful
information.

Here, we simply highlight a few relevant items to set the stage.

Every entity in wireguard is a *peer*. And *peers* interact with each other.
The way they interact is determined by the config files.

Some peers allow others to connect to them at a known hostname or IP address 
and on a specific port. The *endpoint* for this connection is given by
*host:port*.  Any such peer that listens on a known *endpoint* is called a **gateway**. 

Other peers only connect to peer gateways and we refer to these as **clients**. 

Of course gateways may connect with other gateways too. They are still gateways.
So, a gateway is simply a peer that listens on some IP address and port.

Wireguard Config: Interface Section
-----------------------------------

This section is about configs used by wireguard itself.

Each wireguard peer config consists of 2 kinds of components. 

The first part of any peer config is the *Interface* section. 
This specifes the crypto keys and one or more IP addresses 
used by the vpn tunnel.  It may also have a list of DNS servers.

It also has *PostUp* and *PostDown*. Together, these provide a way to have 
a program run when the vpn is brought up and some other program run 
when the vpn is taken down.

These are typically used to set up firewall rules (nftables) and are used
primarily for gateway servers and linux clients. 
We provide more information on these later in the documentation. 

We also provide a sample nftables firewall script which will suffice for 
many/most typical gateway servers. We also provide a linux client program 
which is a DNS helper tool, changing DNS resolution while the vpn is running
and restoring it to it's original state when the vpn is stopped.

Wireguard Config: Peer Section(s)
---------------------------------

The second part of any peer config is one or more *Peer* sections. Each of these
provides the information required to engage with that peer. 
Each peer section has the public key of of the peer.

It also provides the list of networks that are acceptable to use in communicating with that peer.
The available networks are typically internal LANs or internet access. These is the 
*AllowedIPs* variable. It can be one network, a 
comma separated list of networks, and it can be repeated.

Each pair of peers may also share a secret known as a *pre-shared-key* or PSK.
Wireguard's author, Jason Donenfeld, opines that using this provides an additional
security layer facilitating post-quantum resistance. *wg-tool* automatically generates
a unique PSK for each pair of peers that communicate with one another.

The peer section also includes the Endpoint, if that peer is a gateway. 

A client may send all it's traffic to the the gateway it
is using or it may choose to send only the internal LAN traffic to the gateway 
and direcly connect to the internet for the remaining traffic. When the client 
separates the packets like this, it is known as split tunnelling or split routing.

A Note About Shared Networks
----------------------------

Wireguard denotes networks available to each peer using *AllowedIPs*.
That variable tells wireguard to permit packets to from the those networks.
The networks one peer is sharing with another obviously require that the
other peer be willing to share the same network traffic when communicating
with one another.

Wireguard uses *AllowedIPs* to create appropriate routes to network traffic.
For example, if a gateway offers LAN access to it's clients
then clients of that gateway wishing to use that LAN must have 
their *AllowedIPs* include that LAN network.

*wg-tool* generates those *AllowedIPs* that wireguard needs. 
We designed it to minimize user input and to keep those inputs
aligned with physical reality. 

For example, if the Office A gateway offers LAN-A access 
to clients, then *wg-tool* has the gateway designate LAN-A 
available to other peers. When it generates the wireguard configs,
each peer that requests access to that network will have access 
permitted via it's *AllowedIPs*.

*wg-tool* expects each peer to list those networks it offers to 
other peers using the *nets_offerered* variable. 

Of course, this is optional, and is only needed 
with peers that wish to share one or more networks.
This applies to both gateways and clients.

Similarly, peers may request access to one or more networks
by using *nets_wanted*. 

In addition, gateways may set the *internet_offered* flag to indicate
that it will pass traffic to and from the internet on behalf of
it's clients. Clients, in turn, request such access using 
the *internet_wanted* flag.

Based on that information, *wg-tool* generates
the appropriate *AllowedIPs* in the wireguard configs.


Peer to Peer
------------

By default peers are only permitted to communcicate with gateways. If it 
is desirable to allow peers to communicate with one another then this is easily
achieved. Please see the *peer_to_peer* vpn info variable 
in the :ref:`Editing` section for more detail.


Migrating from earlier versions
===============================

Versions prior to the **8.0** can be migrated to the new format with 
*wg-tool --migrate*.

The migration leaves all earlier data files, including the output wireguard configs, untouched.
The current version uses different directories (*Data* and *Date-wg*) to guarantee this.

Importing from standard wireguard configs
=========================================

For those with existing wireguard setup, 
*wg-tool* can import standard wireguard configs. 
Once imported then *wg-tool* can be used to manage things going forward. 

For more info please see :ref:`wg-import`.

After all the configs are imported, its helpful to compare
the resulting generated configs (in *Data-wg*) with those that were imported.

.. _Simple-example:

Simple Example
==============

Lets do a really little example that illustrates how easy it is
to generate wireguard configs. The goal here is to:

* Create a vpn called *vpn-test*
* Add an account called servers with a gateway called *wg-A* 
* Add an account called *alice* with a laptop profile.
* Add an account called *bob* with a laptop profile.
* Do this in the current directory.

.. code-block:: bash

   wg-tool -wkd ./
   wg-tool -new vpn-test
   wg-tool -new vpn-test.servers.wg-A
   wg-tool -new vpn-test.alice.laptop vpn-test.bob.laptop

Add the endpoint the gateway server will be available on:

.. code-block:: bash

   wg-too --edit vpn-test.servers.wg-A

Edit the file (name will be displayed) and change the Endpoint to something like:

.. code-block:: none

   Endpoint = "vpn.example.com:51820"

Then merge the change:

.. code-block:: bash

    wg-tool --merge <filename>

All the wireguard configs will be found under the *Data-wg* directory.
This has the gateway server config along with both users' laptop configs.
