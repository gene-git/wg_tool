
.. _Editing:

Editing and Making Changes
==========================

There are 2 classes of things that can be modified: the vpn information itself and any profile.
Changes are made by using *--edit* option which writes a file. After any changes
to that file they can be merged back using *--merge* option. 

Files to be edited are written into files in the *Edits* directory. *Edits* is located 
in the working directory. Files use TOML format.

TOML, loosely speaking, has *key = value* pairs. Value can be an array
which is simply comma separated list of items inside square brackets *x = [item1, item2, ... ]*.
It can also have named sections which are started with [name]. Everythin following
a named section belongs to that section until a new section is encountered. For additional
infomation please see TOML documentation https://toml.io/en.

Each peer is identified by it's *ID* which is 3 tuple : *<vpn-name>.<account-name>.<profile-name>*.
When editing the vpn itself, the *ID* is just the *<vpn-name>*.

Note that in order to rename something, then please see the *--rename* command line option
which handles this.


Modifying Vpn Information
-------------------------

For example, to modify a vpn named *vpn-test*.

The first step is to make the edit request:

.. code-block:: bash

   wg-tool --edit vpn-test


This creates a file under the *Edits* directory and the filename is displayed.
In this example the file will be *Edits/vpn-test-info.mods*.
The file is in standard TOML format. 


You can then edit the contents of the file that contains the following
items:

.. code-block:: none

   name = "vpn-test"
   tag = "... do not change this ... "
   dns = [
        "dns.exmple.com",
        "dns.example.net",
    ]
    dns_search = []
    peer_to_peer = false
    networks = [
        "10.77.77.0/24",
        "fc00:77:77::/64",
    ]

Never modify the *tag* as it is a unique identifier that determines where to merge any changes.

Most fields are self explanatory. If this is a new vpn then it is fine to change the networks
but be cautious touching this once peers have been added. The code will refuse to remove 
a network if there are existing profiles with IP address assigned from it.

The peer_to_peer flag is discussed in a little more detail below.

After any changes are made the file they can be merged back using:


.. code-block::

   wg-tool -merge <filename>

The will update the config files with support for peer to peer communications.

.. _dns-note:

Note On DNS
^^^^^^^^^^^

We use two variables to capture dns information. *dns* which is the list of 
dns servers and *dns_search* is the list of dns search domains.

Each host in *dns* may be an IP address or a hostname. Any hostname will
use local DNS to resolve this to an IP address before they are output
to the wireguard configs.

This applies not only to the vpn info, but equally to 
dns information used in profiles.

The reason for this, is that wireguard uses it's *DNS* variable for both
dns servers as well as search dommains. It distinguises between them
by recognizing IP addresses.

In a wireguard config, each element of *DNS* will is treated as a dns server only 
if it is a valid IP address (IPv4 or IPv6). Everything else is treated 
as a search domain.


Peer to Peer
^^^^^^^^^^^^

If the *peer_to_peer* flag set to *true* then peers are permitted to communicate with
one another using tunnel IP addresses. By default this is turned off and peers can only 
communicate with gateways. This can be changed at any time.

The gateway will need to have IP forwarding turned on.
Standard way to do this in linux:

.. code-block::

    # /etc/sysctl.d/20-wireguard.conf
    net.ipv4.ip_forward = 1
    net.ipv6.conf.all.forwarding = 1

    # manually turn on if not already
    echo 1 > /proc/sys/net/ipv4/ip_forward
    echo 1 > /proc/sys/net/ipv6/conf/all.forwarding


Peer to peer can be turned off at any time, simply edit as above and set
*peer_to_peer = false* and *merge* the change as usual.

Modifying Profile Information
------------------------------

Any profile, gateway or client can be modified by edting it's ID.
The process is the same as for the vpn above using *edit/merge* but
now using the profile ID.

We illustrate for the peer *vpn-test.user-3.laptop*.

.. code-block:: bash

   wg-tool --edit vpn-test.user-3.laptop

Again, a file is created which you can edit and merge. In this example the file is
*Edits/vpn-test.user-3.laptop.mods* which contains, aside from some comments at the top:

.. code-block:: none

   PersistentKeepalive = 0
   MTU = ""
   post_up = []
   post_down = []
   nets_offered = []
   nets_wanted = []
   internet_offered = false
   internet_wanted = false
   Endpoint = ""
   Endpoint_alt = ""
   dns = [ "dns.example.com", ]
   dns_search = []
   dns_linux = false
   use_vpn_dns = true
   active = true
   hidden = false

   # change to tag = xxx
   # keep id_str ??
   [ident]
   tag = "af4f6d5e-ae66-4bd1-afec-a7037cdd1d9e"


Once again, do not modify the tag. It is a unique identifier used to ensure edits go to
the correct place.

If you need to rename an account or profile, then the *--rename* option should be used.

Most of the other items can be modified and are largely self-explanatory. Where appropriate
we quote from the wireguard documentation.

* no_psk_tags
  
  This is a legacy tag used as part of migration only. It allows old migrated
  profiles that were not using pre-shared keys. Leave this one alone. 
    
* PersistentKeepalive
  
  Per the wg docs: it is the seconds interval, between 1 and 65535, indicating how often to 
  send an authenticated empty packet to the peer for the purpose of keeping a stateful 
  firewall or NAT mapping valid persistently.

  Usually not needed, but if set 25 seconds is a sensible value.

  A good rule of thumb is if this peer only connects to other peers then this is unncessary.
  However when the peer needs to be available to be connected to, then it can be helpful
  to set this. For example, if this peer starts wireguard and sits behind one or more NAT
  routers, and is available for ssh to login, then setting keep alive will ensure 
  there is a viable pathway from this peer to the gateway. This will make sure
  that you can ssh in to this peer.

  See *man wg* for more information.

* MTU

  If not specified, the MTU is automatically determined from the endpoint addresses or 
  the system default route, which is usually a sane choice. However, to manually specify 
  an MTU to override this automatic discovery, this value may be specified explicitly.


* post_up / post_down

  List of scripts to be run after setting up to tearing down the vpn interface.
    
  Gateway example:

.. code-block:: none

  post_up = ['/usr/bin/nft -f /etc/wireguard/scripts/postup.nft']
  post_down = ['/usr/bin/nft flush ruleset']

* nets_offered / nets_wanted

  If this peer offers access to one or more networks, aside from internet, they can be listed here.

  Example providing access to a local network:

  nets_offered = ['192.168.1.0/24']

  Similarly if a peer wants to gain access they it lists the networks in net_wanted.
 
* internet_offered / internet_wanted

  Gateways may allow clients to have their internet traffic flow via the gateway.
  If that is allowed, then set *internet_offfered = true*.

  If a client wants use a gateway for all it's internet traffic, then it sets
  *internet_wanted = true*

  These are mutually exclusive, and gatways ignore internet_wanted, while clients ignore
  internet_offered.
 
* Endpoint
 
  Gatways use this to provide their host:ip. For example:
 
  Endpoint = "vpn.example.com:51820"

* Endpoint_alt

  A gateway may be available on and alternate endpoint. Typically this
  is an internal host or IP and this is directed at admin wishing to test
  the server on the internal network. With this added, you may then 
  mark a profile with *alternate_wanted = true* and an separate wireguard
  config will written to the "Alt" subdirectory. e.g. If a user has a
  desktop profile so marked, then 2 configs will now be written instead of one.
  The only difference is the Endpoint used for the gateway.

.. code-block:: none

   Data-wg/vpn-test/user-1/desktop.conf
   Data-wg/vpn-test/user-1/Alt/desktop.conf

* dns / use_vpn_dns / dns_linux/ dns_search 

  Dns servers, list of hosts or IPs, can be provided in 3 places:

  * vpn info : DNS variable
  * gateways : DNS variable.
  * client's own DNS variable.

  Dns servers are listed in order:

    current profile -> gateways -> vpn info

  Client profiles may toggle the flag *use_vpn_dns = false*, in which case
  they do not use dns servers provided by gateways or vpn info.

  dns = ["dns.example.com",]

  When *dns_linux* is not set, then the list of dns servers will be 
  written to wireguard config [Interface] section.

  If a linux client has *dns_linux = false*, then the resolv.conf will be managed
  by resolvconf (See man wg-quick for more info).

  Use *dns_linux = true* to activate the DNS helper scripts for linux clients.

  These use the dns servers together with any dns search domains as arguments to the
  helper script which is written to the
  postup/postdown variables. 

  *dns_search* follows the same inclusion logic as dns servers: profile -> gateways -> vpn info.
  Note that *dns_search* is only available for linux clients using the dns helper script.

  The dns script should be installed in */etc/wireguard/scripts/wg-peer-updn*.

  Please see :ref:`dns-script` for more details.

  Any linux client using the script will have the dns servers and dns domain search
  set as arguments and written to the resulting wireguard config *postup / postdown*
  variable.
  

  The DNS servers and domain search list are specified in vpn info and
  may be modified with *wg-tool --edit <vpn-name>*.

* active / hidden

  Profile may be marked active, inactive or hidden. Inactive profiles remain in the database
  and visible with *--list* but they are excluded from generating wireguard configs (*Data-wg*).
  hidden are treated as inactive but do not show with *--list* option unless *-verb* is also used.
  These states may be set during editing of a profile, or using the commmand line options.
  Command line options are helpful for quick changes or for changes to more than one profile.
   
  See :ref:`Options-section`.
 
* [ident]

  Dont touch this section which only contains a *tag*. This is a unique identifier
  and is used to ensure that any modifications go to the correct place.
  
  ID names can be changed using the *--rename* option and copies of profiles can be 
  made with the *--copy-from* options.

  See the :ref:`Options-section` for more details.

