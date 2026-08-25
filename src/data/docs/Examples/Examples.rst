
.. Table Centering for latex

.. rst-class:: centered-table-text

.. _Examples:

Working Examples
================

Working examples often provide a good learning path. Here we offer three
such examples, each offering a step by step
illustration how to achieve each goal. 

Examples are found in *src/tests*. The output wireguard configs are 
saved to the *Data-wg* directory. The *Data* directory is the tools
private database; the data files are all ascii text.

For each example, the goal is specified and then executed using 
*wg-tool* to achieve that goal.

Once each example completes, the standard wireguard configs are produced and 
saved in the *Data-wg* directory.

Examples must be done in order. The *./run-tests* script runs all examples
sequentially and checks the outputs against expected *Baseline* results.

The first example is the simplest.  It uses a single gateway, *wg-A*, and three 
road warrier clients.  The gateway provides it's clients with access to 
*Office A LAN* and an option for their internet traffic to go via the
gateway.

The second example extends this by adding a second gateway, *wg-B*.
This new gateway provides access to a second *Office B LAN*. 
Clients now access *Office A LAN* via gateway *wg-A* and *Office 
B LAN* via gateway *wg-B*.

The third example modifies gateway *wg-B* to now be a client. This client connects 
to gateway A and still provides *Office B LAN* access but now directly only to gateway *wg-A*
which in turn offers access to it's own clients.

Gateway *wg-A* is now able to provide access for road warrier clients to 
both *LAN A* and *LAN B* with assistance from the *client wg-B*.

The fourth example demonstrates restriced LAN access using an *IP Group* called *admin*.
Only members of the *admin* group are given access to the LAN.

I would encourage you to work through the examples. But,
if you want to quickly see the results of doing the examples, there are
scripts in the examples directory that do it for you.
The scripts generate the data in the same directory they are run in.

.. code-block:: none

   create-example-1
   create-example-2
   create-example-3
   create-example-4

These can be run sequentially starting with *create-example-1*.
You can then run *create-example-2* and *create-example-3*. After each step 
you may want to look at the outputs saved under *Data-wg* and get 
a summary using:

.. code-block:: bash

   wg-tool -lv

Where to Run The Gateway
------------------------

While gateways can be run on a firewall / border router, we prefer to run them
behind the firewall, where the firewall forwards necesary UDP port.

The reason we like this approach is that firewall rules used by the gateway
don't have to be concerned about any existing firewall rules, as is the case 
when gateway runs on the firewall itself. It's also a little cleaner from a security
perspective to minimize what runs on the firewall.

One downside putting the vpn behind the firewall is that internal hosts 
wishing to use the gateway, may need additional routes. 

For example, if LAN-A clients wish to access LAN-B, they will
need a route to the appropriate vpn gateway to allow this.

In contrast, when the vpn runs on the firewall, since the firewall
is typically the default route, additional routes may not be needed.

Adding static routes in linux is straightforward.

For DHCP, ISC's Kea supports
classless static routing [#rfc3442]_. In Kea this takes a list of routes, each of the
form: 

.. code-block:: none

    network - IP-address

which signifies that the route to *network* is provided by *IP-address*.
Per the RFC this option supercedes the older routers option 
and thus all routes should be listed in addition to having the older option.

If the gateway runs on the firewall, and LAN clients have a default route to the firewall,
then it all works without any additional route.

For the working examples, exactly where the gateways run plays no role at all.

On to the examples!

.. rubric:: Footnotes

.. [#rfc3442] https://datatracker.ietf.org/doc/html/rfc3442


