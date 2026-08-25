
.. _migrating:

Migrating from Earlier Version
==============================

Version *8.x* introduces significant changes including with the
database file formats. This section discusses migration
from earlier versions of *wg-tool* to the current version.

If you have not used *wg-tool* and would like to import existing
standard wireguard configs, then see :ref:`wg-import` instead.

Migration from an earlier version is pretty much automatic.

In the earlier versions gateways were known as servers and accounts
were called users. 

In current version each item has an identity comprised of 3 parts:

* vpn name
* account name
* profile name

And would be denoted by, for example: *vpn1.alice.laptop*.
The directory file hierarchy follows this.

N.B.

* All existing data is untouched.
* New data lives in different directories.

After migration, the older (pre *8.x*) directories (*configs* and *wg-configs*) may be deleted 
when convenient. 

All tool data now resides under *Data* and standard wireguard configs are output 
under *Data-wg*. 

To migrate existing data, run:

.. code-block:: bash

   wg-tool --migrate

All being well this should populate both *Data* and *Data-wg*. You can examine the 
wireguard configs under *Data-wg* and you can see a list of all 
accounts and their profiles using:

.. code-block:: bash

   wg-tool --list


Gateway with Alternate Endpoint
-------------------------------

If you had an alternate endpoint in the gateway profile it will be now be in the
the *Endpoint_alt* field. 

If you had any clients using the alternate endpoint then you can now mark a profile 
using *alternate_wanted = true*. When this is set for some profile, then a second
wireguard config will be created using the alternate endpoint. That config is identical
to other than the Endpoint.

For any such profiles you'll need to do this step manually after the migration.
In order to change a profile this way you use the *--edit* option.

For more detail please see :ref:`Editing`.

.. code-block:: bash

   wg-tool --edit vpn1.alice.laptop

Which creates a regular file and displays the filename. In this example it would be

.. code-block:: none

   Edits/vpn1.alice.laptop.mods

You then edit the file with any text editor and change 

.. code-block:: none

    *alternate_wanted = true*. 

The change is merged back using:

.. code-block:: bash

   wg-tool --merge Edits/vpn1.alice.laptop.mods

At this point any profile with *alternate_wanted = true* will have a new
config saved in the "Alt" subdirectory where the profile is.

For example, here we would find:

.. code-block:: none

   Data-wg/vpnt/alice/laptop.conf
   Data-wg/vpnt/alice/Alt/laptop-alt.conf

and the associated QR code image file under *qr* directory.

After this is done, you may want to mark any older profiles using this
altenate Endpoint as *hidden*, since they are no longer needed.


.. code-block:: none

   wg-tool --hidden vpn1.alice.<no-longer-needed>

Where the *<no-longer-needed>* would be replaced by whatever profile name
is not needed.

Using DNS Instead
^^^^^^^^^^^^^^^^^

If an alternate endpoint uses a domain name, then the best approach is to
have the local DNS server map that host name to it's internal IP address 
when seen on the internal network, and the usual public IP when on the outside. 

This way there is no need for any additional client configs at all.
Having clients use *alternate_wanted* is really only useful when the 
local DNS option is not available.

Hiding Unused Profiles
------------------------

For all available options run *wg-tool --help* or see the section :ref:`Options-section`.

Since this may come up after migrating, a brief mention of this functionality may 
be useful.

If you you have profiles that are no longer needed they can be marked *not-active*
or *hidden*. In both cases, wireguard configs are no longer generated 
and all data is retained in case of need in the future.

If a profile is marked hidden then it remains hidden with *--list* unless *--verb* 
is also used.
If it's marked not active, then it will always be visible when listing profiles *--list*.
Profiles that are not active or hidden do not get a wireguard config generated.

for example:

.. code-block:: bash

    wg-tool --hidden vpn1.alice.laptop

The active/hidden states may also be changed when *editing* a profile.
