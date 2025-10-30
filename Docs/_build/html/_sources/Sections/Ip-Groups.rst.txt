.. _Ip_Groups:


IP Groups
=========

There are situations where a group of peers needs special handling. For example,
one group of peers might have special privileges, lets say *admin* privs, and 
a set of peers needs to permit access to that group of peers only.

This is where ip groups are useful. Wireguard provides access control via it's *AllowedIPs*
setting. While this is a bit limiting, it does provide an *IP* based mechanism for us to use.

We define our *admin* group by a set of IPs that are a subnet(s) of the 
vpn network(s). 

Note, that setting a peer profile with a group membership, necessitates that it's
internal vpn IP must be changed to one that is part of that *ip group*. In turn, this
means a new wireguard config for that peer.

For example, let the vpn network use these networks:

.. code-block:: none

   10.77.76.0/22
   fc00:77:77::/56


Remember you can always expand the vpn networks IP range by simply doing *--edit* <vpn-name>, 
and then modifying the *networks:* setting to expand the network. 
See :ref:`Editing` for more information on that.

The set of ips for an IP group must include both the IPv4 and IPv6 vpn networks above. 
If the vpn is using both of course.

These subnets work nicely for our *admin* ip group:

.. code-block:: none

   10.77.79.224/27
   fc00:77:77:fe::/64

Then any peer profile that is marked as a member of the *admin* ip group, will have its vpn IP
taken (or changed if necessary) to be from those subnets. 

Please note, as usual, any IP belonging to the vpn network or broadcast address(es) is 
always excluded. In the example at hand, the admin ip group *10.77.79.224/27* has a usable range *10.77.79.224 - 10.77.79.254*, 
since the last IP, *10.77.79.255*, is the broadcast address of the vpn network *10.77.76.0/22*

In this case admin group can have up to 31 members, as there are 31 available IP addresses in the
subnet 10.77.79.224/27 (after excluding the on unusable IP).

Let us add the *admin* ip group using the subnets shown above to the vpn named *vpn-test*:

.. code-block:: bash

   wg-tool --add-ip-grop admin "10.77.79.224/27,fc00:77:77:fe::/64" --ident vpn-test

Thats' all that's needed to define this ip group.

The next step is to add members to the group.
For example, to make vpn-test.users.sally a member of *admin* group we can do so using:

.. code-block:: bash

   wg-tool --ip-group admin vpn-test.userts.sally
    
The final step is to use the *admin* group to do something. 

For example, let's have the *vpn-test.customers.abc-corp* allow access 
to members of admin ip group.

.. code-block:: bash

    wg-tool --allow-ip-groups admin vpn-test.customers.abc-corp

This change does require the peer *vpn-test.customers.abc-corp* to get a new config since their
settings have now changed. In addition to modifying existing profiles, 
both *--ip-group* and *--add-ip-group* can be used 
at same time as creating a new peer profile.

Important Security Considerations
---------------------------------

To maintain the desired security restricitions for peers that limit access to an ip group, 
it is important that the following options are disabled. 

Both will be automatically disabled for any
peer that has activated *allow-ip_groups*. They can also be manually disabled:

* **peer_to_peer** feature must be disabled 

  This is a vpn wide setting that allows any peer to peer communication. Obviously,
  this should not be permitted when restricting access to some ip group(s).

  This is disabled by default but can be manually changed with *--edit <vpn-name>*.

* **internet_wanted**

  Must be off for any peer limiting access using *allow-ip-groups*.
  Allowing access to the internet allows any access from/to any IP address, which
  can include other peers.

  While this is featire is enabled by default, using *allow-ip-groups* will 
  automatically disable it.

* avoid *LAN* access

  If there is any possibility of overlapping LAN networks, they should not be accessible via
  the vpn. Avoid sharing any LAN access over the vpn.

