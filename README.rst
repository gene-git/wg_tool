.. SPDX-License-Identifier: MIT

#######
wg-tool
#######

Overview
========

Manage wireguard server and user configs. Ensures server and user configs remain consistent.

Available on 

 * `Github`_
 * `Archlinux AUR`_

On Arch install using the PKGBUILD provided in packaging directory or from the AUR.

Key features
============

 * simplifies wireguard administration. ( server and users )

 * guarantees server and user configs remain synchronized.

 * handles key creation when needed

 * users can have multiple profiles (bob:laptop bob:phone etc)

 * users and/or profiles can be marked active/inactive 

 * takes output of 'wg show' and shows connections by user/profile name.  
   This solves a long standing annoyance in a simple way by showing names 
   not public keys.
   Provides check that server is up to date and may need restart 
   with new wg0.conf

 * supports importing existing user/profiles

New
===

 * New Feature: Multiple IP Address for user profiles.

   See new options *--prefixlen_4* and *--prefixlen_6*.

   I'd appreciate testing and feedback (see Issue #14)

   New user profiles now get ip(s) from each server network. 
   CIDR address for each network will have prefixlen_4 or IPv4 and prefixlen_6 for IPv6 networks.
   prefixlen are settable with new options.
   
   Existing user profile (or -all) can have their IPs refreshed to pick up their new IPs from
   server config. If you already have multiple networks or simply added them to the 
   server *Address* variable in *configs/server/server.conf* - and then refresh using:

.. code-block:: bash

   wg-tool -mod -ips <user>:<profile>

or

.. code-block:: bash

   wg-tool -mod -ips -all
.. 

 * New option *-upd, --upd_endpoint* used with *-mod* to update existing user profiles when server
   IP/Port is changed.

 * *-mod* now supports *-all* to apply to all users.

 * `wg-client`_ companion package now available. A linux client tool and separate graphical 
   program to launch wireguard client. Simplify using wg for all users.

 * wg-peer-updn now saves additional copy of dns file as resolv.conf.wg
   Helpful for clients which sleep and on resume network restart overwrites resolv.conf
   This makes it simple to put back the vpn resolv.conf file by
   copying resolv.conf.wg to resolv.conf.  Used by wg-client package.
   Postdown will still restore original resolv.conf.save as usual.

 * Change python build from poetry to hatch

 * Can now generate html and pdf docs using sphinx
   Pre-built wg_tool.pdf provided in repo
   See *Howto-Build* in the *Docs* directory

Interesting
===========

The Wireguard server report shows users by user:profile names
instead of by public key fingerprint.

Can get human readable server report based on output of *wg show*.
Can do this either by running on the wg server (*-rrpt, *--run_show_rpt*) 
or from saved report file *(*-rpt*, *--show_rpt*).

This report shows users and profiles in nice human readable form.

It also indicates whether each user and profile are marked active 
(by showing (+) or (-) beside the name. If an inactive user 
is connected, it may be time ensure the server is running the latest wg0.config.

This feature solves a long standing problem with native wireguard reports which 
burden the administrator with mapping IPs or public keys to a user profile. 
The report does it for you and shows actual user and profile names.

Because of this feature, this tool eliminates any need for schemes, 
such as Vanity keys, attempting to map public keys to something more palatable.

It will also advise if the current server config being used is out of 
sync with current tool config and therefore needs updating and/or restarting

Sample output of *wg-tool -rrpt* ::

    wg server:
       interface : wg0
            port : nnnnn
         pub_key : <x>

       susan (+) : phone (+)
        endpoint : xxx.xxx.xxx.xxx:yyyyy
         address : xxx.xxx.xxx.xxx/32
       handshake : 2 hours, 4 minutes, 15 seconds ago
        transfer : 102.62 MiB received, 320.29 MiB sent

More background
===============

The tool manages wireguard server and user configs.

It also guarantees that server and user configs are kept properly synchronized.  
It handles key creation whenever needed, such as when adding user/profiles or 
when doing key rollovers.

A wireguard server and user configs share several common variables, such as public keys, 
hostname and listening ports, and therefore it's crucial they are consistent.

wg-tool uses a single source of data which is used to populate the actual 
configs wireguard needs; this approach  guarantees they are always consistent
with one another. It also simplifies managment significantly. Common tasks are
handled by the tool in a convenient way. For example, It is very 
straightforward to add users or user profiles, roll keys or make users or profiles
active or inactive.

In a nutshell to setup and use wireguard vpn one needs a server and each client 
gets a configuration, either in the form of a text based *.conf* file or
a QR code. QR codes work nicely for wireguard phone app, for example, where the 
app uses on board camera to read the the QR code. For computer clients, the conf file 
is the simplest. The server and client keys share common information which must be kept
synchronized. This includes shared public keys, pre-shared keys for added security
along with network information (IPs, Ports and DNS).

wg-tool uses a file based configuration database kept under the *config* directory.
This provides all the inputs the tool needs to generate the server and client configs.
The latter are saved into the *wg-config/server* and *wg-config/users* directories 
for the server and clients respectively.

For convenience, previous configs are saved with *.prev* extension making it easy
to compare with a prior version. It can be useful after making changes to
diff the two configs.

The wg server config, *wg-config/server/wg0.conf* should be installed, as usual, 
in /etc/wireguard. 

Each user can have 1 or more profiles. For example bob may have *bob:phone* and 
*bob:laptop*.  The configs to share with each profile is saved into, in this example,
*wg-config/users/bob* as bob-phone.conf, bob-phone-qr.png, bob-laptop.conf and bob-laptop-qr.png.
These are provided to the user - bob in this case.

For those computer clients running Linux, there are 2 kinds of configs available. 

 * standard config

    where the DNS infomation in config is used by wg-quick. wg-quick, in turn, relies on resolvconf.

 * linux config

    this is my preferred approach. Activated by the *--dns_linux* option. When 
    using this, wg-quick uses the provided *wg-peer-updn* script via PostUp/PostDown. 
    
    This scipt saves the current dns resolv.conf file when VPN is brought up using *wg-quick up*, 
    installs the VPN dns into /etc/resolv.conf and restores the prior resolv.conf when VPN is 
    deactivated (wg-quick down).


Directory and File Structure
============================

There are 2 kinds of config files. We use the following convention:

 * **wg-configs** : configs used by wireguard itself

    These are the outputs of *wg-tool*. 

 * **configs** :  configs used by wg-tool 

    These are the inputs for *wg-tool*

For example, the wireguard server config file, wg0.conf, will be located 
in ::

    wg-configs/server/wg0.conf

And the user QR codes and *.conf* files will be under ::

    wg-configs/users/

Laying out this directory structure in a bit more detail.

*wg-tool* configs ::

    configs/
           server/
               server.conf
           users/
               user-1/
                   user-1.conf
               user-2/
                   user-2.conf
               ... 

*wireguard* configs will be placed ::

    wg-configs/
              server/
                    wg0.conf
              users/
                    user-1/
                        user-1-profile-1.conf
                        user-1-profile-1.png
  
                        user-1-profile-2.conf
                        user-1-profile-2.png
                        ...
                    user-2/
                        user-2-profile-1.conf
                        user-2-profile-1.png
  
                        user-2-profile-2.conf
                        user-2-profile-2.png
                    

Each of the files is actually a symlink to the real file which is kept under 
a *db* directory at the same level as the symlinks. 

This allows us to keep history of every config as far back as we choose. There are options
to choose the amount of history to keep for configs and separately for wg-configs. 
The default, in addition to current values, is to keep 5 additional configs 
and 3 wg-configs.

Whenever a config file is changed the previous version is made available 
as a symlink named *xxx.prev*. This allows for straightforward comparisons and makes it easy
to revert if that were ever needed; though it is pretty unlikely to ever be
the case. 

Each user can have multiple profiles - each profile provides separate
access to the vpn. As an example, user *jane* may have a *phone* profile and 
a *laptop* profile. Each profile will provide the wireguard .conf file along 
with an image file of its QR code. These 2 files provide the 
standard wireguard configs for users.

Aside from the QR image files, all text files are in standard TOML format.

###############
Getting Started
###############

Using wg-tool for first time
============================

There are 2 ways to get started; either create a new suite of users/profiles or 
import existing wireguard user.conf files.  You can add users or new profiles for existing users
at any time. This is very easy and explained below using the *--add_user* option.
You can also import a user at any time, though it's primarily useful when first
setting up wg-tool.

If you already have wireguard running then importing is the simplest and best way to proceed.
If you're starting from scratch then wg-tool will create new users and profiles for you.

Either way it's pretty straightforward.

Step 1 - Create Server Config
-----------------------------

In either case the first step is to create a valid server config file.
The best way to do that is to run::

        wg-tool --init
 or
        wg-tool --work_dir=xxx --init

By default, when initializing,  work_dir will be */etc/wireguard/wg-tool* if it exists and with 
appropriate access permission (i.e. root), otherwise the current directory *./*.

This creates a template in: *configs/server/server.conf*.

This file must be edited and changed to reflect your own network settings etc.
These are all wireguard standard fields. 

The key fields to edit are:

 * Address  

   This is the internal wg cidr mask on the server IP addresses (IPv4 and IPv6).  
   N.B. If you prefer user:profile get IPv6 then put it first in the list.

 * Hostname and ListenPort  

   wg server hostname as seen from internet and port chosen 

 * Hostname_Int ListenPort_Int  

   wg server hostname and port as seen on internal network.   
   Useful for testing wg while inside the network.
   Client configs created with the *-int* option of **wg-tool** will use this internal server:port.

 * PrivateKey, PublicKey  

   If you have exsiting wg server, change these to your current keys.  
   If not they are freshly generated by --init. and can be safely used.

 * PostUp PostDown  

   If you want to use the nftables provided by wg-tool - just copy postup.nft from the scripts directory.
   Change the 3 network variables at top for your setup.

 * DNS   

   List of dns servers to be used by wg - typical VPN setup uses internal network DNS 

postup.nft
^^^^^^^^^^

The nftables sample script, scripts/postup.nft, should be copied to 
/etc/wireguard/scripts.

Remember to edit the network variables at the top of the *postup.nft* script to match your network.
One common case  is to provide users with access to internet as well as to the internal network. 
The system border firewall must forward vpn traffic to the wireguard server which running on 
inside protected by the firewall.

The *postup.nft* script provides access to the internet and lan provided the wireguard server 
host has that access.  
If the wg server is in the DMZ then it probably only has access to DMZ net and internet. 

Before deploying the *postup.nft* script, edit the 3 variables at the top for your own 
server setup:

 * vpn_net  

   this cidr block must match whats in the server config

 * lan_ip lan_iface  

   IP and interface of wireguard server

Remember to allow forwarding on the wireguard server, to ensure VPN traffic 
is permitted to go to the LAN::

        sysctl -w net.ipv4.ip_forward=1

to keep this on reboot add to */etc/sysctl.d/sysctl.conf* (or other filename)::

        net.ipv4.ip_forward = 1

The list of active users is managed in the *server.conf* file.
This is generated and updated by wg-tool. The tool provides options to add and remove
users from the active list. If a user is markewd inactive, none of their profiles will be in server
wg0.conf. If a user is active then only their active profiles will be provided to wg0.conf

Each user config has its own list active profiles.  It too is managed by the tool. 

N.B. the active users and active profiles lists, only affect whether they are included
in the server wg0.conf file. No user or profile is removed when a user and/or profile
is marked inactive.

Step 2 - import and/or add users and profiles
---------------------------------------------

Now that the server config is ready, we can add users and their profiles.

Each user can have 1 or more profiles.  Each user's data, including all
their profile info, in kept in a single config file.
It also tracks the list of active profiles.

If a profile is active, it will be put in wireguards wg0.conf server config,
otherwise it won't.

Wireguard QR codes and .conf files are always created for every user/profile
regardless of whether it is active or not.

Since each user has their own namespace, profile names can be same for different users.

Adding new users and profiles
=============================

Users and profiles can be created at any time. They can be created in bulk 
or one user at a time. For example this command::

        wg-tool --add_user bob:phone,desk,ipad jane:phone,laptop

creates 2 users. *bob* gets 3 profiles : phone, desk and ipad while 
*jane* gets 2 profiles: phone and laptop.

If you don't provide a profile name, the default profile name is *main*.

At this point you should now have server config supporting these 5 user profiles
and the corresponding wireguard QR codes and .conf files under wg-configs/users

You can get list of all users and their profiles ::

        wg-tool --list_users

The (+) or (-) after a user or profile name indicates active or inactive.

Importing existing users and profiles

The tool can import 1 user:profile at a time. This is done using::

        wg-tool --import_user <user.conf> user_name:profile_name

where \<user.conf\> is the standard wireguard conf file (the text version of the
QR code). And the user_name and profile_name are what you want them to be known 
as now.  

What worked for me was to copy all those existing wireguard user.conf files 
into ./old/ and then make a little shell script like the sample scripts/import_users.
Script just imports each profile 1 at a time.

Then run the shell script. End result should be working wg0.conf
functionally identical to what you currently have. In addition
a new set of user-profile.conf and associated qr codes. All found in
*wg-configs/*

As above you may want to see a list of users/profiles::

        wg-tool --list_users

And compare a user profile conf or 2 with existing ones - QR codes will be different, but contain the
same information. You can check this for bob's laptop QR by doing this::

    zbarimg wg-configs/users/bob/bob-laptop-qr.png

which is available in the zbar package. It should match the corresponding user.conf file 
in *wg-configs/users/bob/bob-laptop.conf*


Managing Users/Profiles 
=======================

I recommend avoiding manually editing any config files, but if you do for some reason, 
then run *wg-tool* with no arguments. It will detect the changes and update *wg-configs*.

Pretty much everything you need to do should be available using wg-tool::

        wg-tool --help

gives list of options.

Options
-------

Many options take user/profiles as additional input. 
users/profiles are to be given on command line ::

    user
 or
    user:prof
 or
    user_1:prof_1,prof_2 user2 user_3:laptop,tablet

Summary of available options:

Positional arguments:  

 * users  : user_1[:prof1,prof2,...] user_2[:prof_1,prof_2]

Options:

 * (*-h, --help*)

   Show this help message and exit

 * (*-i, --init*)

   Initialize and creat server config template. 
   Please edit to match your server settings.

 * (*wkd, --work_dir <dirname>*)

   Set working directory.  
   This is is the directory holding all configs.

   By default: 

     + when used with *--init*, work_dir will be */etc/wireguard/wg-tool* if the directory exists and 
       with appropriate access permission (i.e. root), otherwise the current directory *./*.

     + if not initializing, then, with access permission,  */etc/wireguard/wg-tool/* will be 
       the work_dir if there is a *config* dir in it, otherwise it is set to current dir *./*.

 * (*-add, --add_users*)

   Add user(s) and/or user profiles user:prof1,prof2,...

 * (*-mod, --mod_users*)

   Modify existing user:profile(s).  Use with *-dnsrch*, *-dnslin*, and *upd*
   Can apply to all users/profiles via the *-all* option.

 * (*-pfxlen_4, --prefixlen_4*)

   User profiles now get IP Addresses(es) from each server network. Each address
   is a block with cidr prefixlen_4. Defaults to 32 which means 1 IP address.
   e.g. if set to 30 then would get a block of 4 x.x.x.x/30

 * (*-pfxlen_5, --prefixlen_5*)

   Similar to --prefixlen_4 but for ipv6. Default is 128

 * (*upd, --upd_endpoint*)

   Use with *-mod*
   Ensure user/profile is using current server endpoint.  Add *-int*
   if want to use internal hostname/port.

   For example if the server IP changes, then you can update existing user/profiles with

   wg-tool -mod -upd -all

 * (*-dnsrch, --dns_search*)

   Use with *-mod*

   Adds the list DNS_SEARCH from server config to client DNS search list.
   DNS_SEARCH in server.conf should contain a list of dns domains for dns search and 
   Use together with *-add* for new user:profile or with *-mod* with existing profile.

 * (*-dnslin, --dns_linux*)

   Use with *-mod*

   For a Linux client, provide support for managing the dns resolv.conf file.
   What this does is save existing one, install the wireguard dns version and 
   then restore original on exit.
   Use together with *-add* for new user:profile or with *-mod* with existing profile.

   To bring up wireguard as a linux client one uses ::

        wg-quick up <user-prof.conf> 
        wg-quick down <user-prof.conf> 

   This will then use the wireguard DNS while running and restore previous dns on exit.

   To add dns search and use dns_linux on existing user profile. First update the 
   server config by editing *configs/server/server.conf* and add list of seach domains ::

        DNS_SEARCH = ['sales.example.com', 'example.com']

then ::

        wg-tool -mod -dnsrch -dns_linux bob:laptop

By default wg-quick uses resolvconf to manage dns resolv.conf.  If you prefer, or dont use resolvconf
then use this option. But only with Linux - it will not work for other clients (Android, iOS, etc)

With this option the usual DNS rows in in the conf file are replaced with PostUp and PostDown.  
PostUp saves existing resolv.conf, and installs the one needed by wireguard.
PostDown restores the original saved resolv.conf.

To use this the script *wg-peer-updn*, available in the *scripts* directory must be
in /etc/wireguard/scripts for the client. 

The installer for the wg_tool package installs the script - but clients without this
package should be provided both the user-profile.conf as well as the supporting 
script *wg-peer-updn*. 

 * (*-int, --int_serv*)

   With --add_users uses internal wireguard server

 * (*-uuk, --upd_user_keys*)

   Generate new set of keys for existing user(s).
   This is public and private key pair along with new pre-shared key.

 * (*-usk, --upd_serv_keys*)

   Generate new pair of server keys.
   NB This affects all users as they all use the server public key.

 * (*-all, --all_users*)

   Some opts (e.g. upd_user_keys) may apply to all users/profiles when this is turned on.

 * (*-act, --active*)

   Mark one or more users or user[:profile, profile...] active

 * (*-inact, --inactive*)

   Mark one or more users or user[:profile, profile...] inactive

 * (*-imp, --import_user <file>*)

   Import a standard wg user conf file into the spcified user_name:profile_name
   This is for one single user:profile

 * (*-keep, --keep_hist <num>*)

   How much config history to keep (default 5)

 * (*-keep_wg, --keep_hist_wg <num>*)

   How much wg-config history to keep (default 3)

 * (*-sop, --save_opts*)

   Together with --keep_hist and/or --keep_hist_wg
   to save these values as new defaults.

 * (*-rrpt, --run_show_rpt*)

   Run "wg show" and generate report of users, profiles.
   Also checks for consistency with current settings.

 * (*-rpt, --show_rpt <file>*)

   Same as *-rrpt* only reads file containing the output of *wg show*
   If file is name *stdin*, then it reads from stdin.

 * (*-l, --list_users*)

   Summary of users/profiles - sorted by user.

 * (*-det, --details*)

   Adds more detail to *-l* and *-rrpt*.
   For *-l* report will also include details about each profile.
   For *-rrpt* report will show all user:profiles known to running server, not just
   those for which it has a recent connection. 

 * (*-v, --verb*)

   Adds more verbose output.

Note on MTU
-----------

I came across one hotel wifi, that while the vpn worked fine to provide internet access, I found
that for my laptop to be able to also 'ssh internal-host' it would hang::

  ssh -v <host> 

hangs right after this is logged::

    expecting SSH2_MSG_KEX_ECDH_REPLY

The *fix* was to set the MTU from 1500 down to 1400 on my laptop while at that hotel. 
The internet access continued to work fine, but this fixed whatever was a problem for ssh;
so now 'ssh internal-host' worked as usual. 
  
I have only had to change MTU setting at one location, but I mention it here in case 
anyone else comes across this.


Key Rollover
==============

wg-tool makes key rollover particularly simple - at least as far as updating keys
and regenerating user and/or server configs with the new keys. 

Distribution of the updated config/QR code to each user is not addressed by the tool.
Continue to use existing methods - encyrpted email, in person display of QR code etc. ...

Its equally simple to update keys on a per user basis as well - just specify them on
command line. 

To roll the server keys run:

.. code-block:: bash

        wg-tool --upd_serv_keys

This will also update all user profiles with the server's new public key.

To roll all user keys run:

.. code-block:: bash

        wg-tool --upd_user_keys

or as usual you can specify which profiles to generate the new keys for.

.. code-block:: bash

        wg-tool --upd_user_keys  [user:prof1,prof2 user2 ..]

As usual, a change to any user profiles will generate new server wg0.conf file
reflecting whaterver change was made.


########
Appendix
########

Notes
=====

 * Config changes are tracked by modification times.  

   For existing user/profiles without a saved value of *mod_time*, 
   the last change date-time of the config file is used and saved.
   These mod times are displayed when using *-l* and *-l -det* options.

2022-12
-------

 * Stronger file access permissions to protect private data in configs.

 * Changes to work_dir.

   Backward compatible with previous version.
   Now prefers to use */etc/wireguard/wg-tool* if possible, otherwise 
   falls back to current directory.

2022-11
-------

See `Options`_ or for more detail.

 * (*-dnsrch, --dns_search*)  

   Adds the list DNS_SEARCH from server config to client DNS search list.  
   DNS_SEARCH in server.conf should contain a list of dns domains for dns search.  
   Use together with *-add* for new user:profile or with *-mod* with existing profile.

 * (*-dnslin, --dns_linux*)  

   For a Linux client, provide support for managing the dns resolv.conf file.
   What this does is save existing one, install the wireguard dns version and 
   then restore original on exit.
   Use together with *-add* for new user:profile or with *-mod* with existing profile.


Install
=======

While it is simplest to install from a package manager, manual 
installs are done as folllow:

First clone the repo :

.. code-block:: bash

   git clone https://github.com/gene-git/wg_tool

Then install to local directory.
When running as non-root then set root_dest to a user writable directory.

.. code:: bash

    rm -f dist/*
    /usr/bin/python -m build --wheel --no-isolation
    root_dest="/"
    ./scripts/do-install $root_dest

Dependencies
------------

* Run Time :

  * python (3.9 or later)
  * wireguard-tools
  * nftables (for wireguard server postup.nft)
  * tomli\_w (aka python-tomli\_w )
  * netaddr (aka python-netaddr )
  * python-qrcode
  * If python < 3.11 : tomli (aka python-tomli)

* Building Package:

  * git
  * hatch (aka python-hatch)
  * wheel (aka python-wheel)
  * build (aka python-build)
  * installer (aka python-installer)
  * rsync

Philosophy
----------

We follow the *live at head commit* philosophy. This means we recommend using the
latest commit on git master branch. 

This approach is also taken by Google [1]_ [2]_.

License
========

Created by Gene C. and licensed under the terms of the MIT license.

 * SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>

.. _Github: https://github.com/gene-git/wg_tool
.. _Archlinux AUR: https://aur.archlinux.org/packages/wg_tool
.. _wg-client: https://github.com/gene-git/wg-client

.. [1] https://github.com/google/googletest  
.. [2] https://abseil.io/about/philosophy#upgrade-support

