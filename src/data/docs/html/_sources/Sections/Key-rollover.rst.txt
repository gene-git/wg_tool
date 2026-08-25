.. SPDX-License-Identifier: GPL-2.0-or-later


Key Rollover
============

Generating New Crypto Keys
--------------------------

wg-tool makes key rollover particularly simple - at least as far as updating keys
and regenerating user and/or server configs with the new keys.

Each peer utilizes one *private/public key pair*, and the *public* key is shared
with all any peers that it communicates with. 

In addition every pair of peers that communicate with one another 
are assigned a unique pre-shared key (or *PSK*). The *PSK* strengthens the 
security of the communications between that pair and in particular enhances
post-quantum resistance.

When new keys are generated, the peer gets a new *private/public* key pair.
In addition any needed *PSKs* are re-generated.

As usual, after new keys are made, the corresponding wireguard configs 
are automatically updated. This includes any impacted by a change in *PSKs*.

Distribution of the updated configs and QR codes to each user is not addressed by the tool.
Continue to use existing methods - encyrpted email, in person display of QR code etc.

Its as simple to update gateway or client keys - just specify those to change on
command line.

To roll the server keys run:

.. code-block:: bash

        wg-tool --roll-keys <id or id list>

Once this has completed, any affected wireguard configs will be updated appropriately.


