Networking Notes
================

This note is an overview of wireguard networking setup. By default we assume that the wireguard 
server has access to internet and any desired local services.  With this in mind, the
default *postup.nft* script NATs the wireguard network so it's traffic to the LAN
appears to come from the wireguard server itself. We also assume that the local DNS servers
provided in wireguard configs, are available to the wireguard server - typicallu as they are on
the same LAN.

Edit *postup.nft* and set the variables for your network

        define vpn_net = 10.99.99.0/24  # must match server config
        define lan_ip = 10.0.0.1        # real lan ip of wg server
        define lan_iface = eno1         # lan interface
        define wg = wg0



Assumed Network Topology for default postup.nft
-----------------------------------------------

.. code::

   (        |              |                         |          |               | 
   (        |              | (vpn.ip:39001)          |          |               |
   (        |    <--->     | pub-ip           lan-ip | <-NAT->  | lan-ip:39001  |
   (        |              |                         |          | en01          | 
   (        |              |                         |          |               | 
   ( Client |   Internet   |       Firewall          |   LAN    |   WG Server   |

   + ---------------------------------------------------------------------------+
   |     <-->               VPN Tunnel  (10.99.99.x)                <---->      |
   +----------------------------------------------------------------------------+


If your network differs, then adjust the nftables postup rules as needed. 
   
We also assume that there are no other nftables rules running on the wireguard server itself.
If there are then you should change the postdown rule to not flush all rules as happens by default
and instead add the rules and remove them in postdown.
