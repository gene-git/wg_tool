# wg_tool

Tool to manage wireguard configs for server and users.

## Installation

Available on 
 - [Github source ](https://github.com/gene-git/wg_tool)
 - [Archlinux AUR](https://aur.archlinux.org/packages/wg_tool)   
   PKGBUILD also in source tree under archlinux

### dependenceis

  - python (3.9 or later)
  - wireguard-tools
  - nftables (for wireguard server postup.nft)
  - tomli (aka python-tomli)
  - tomli\_w (aka python-tomli\_w )
  - netaddr (aka python-netaddr )
  - python-qrcode

## New or Coming Soon

New:

 - *--show_rpt*   
The output of *wg show* can be passed to wg-tool, either as a filename, or 
use *stdin* (for it read from stdin). It parses it to make a report of 
connected user profiles by name.  Obviously, this has to be run in 
same directory as its configuration files.

The raw output of *wg show* is not terribly user friendly, as wireguard has
no idea about user names or profile names. wg-tool remedies that for you.

Example:

        wg show | wg-tool -rpt stdin

New:

 - *--run_show_rpt*   
Same as --show_rpt, but runs *wg show* for you. This obviously only works 
when run on the vpn server.  

        wg-tool -rrpt


New:

 - *--work_dir*   
Specify the working directory, by default this is current dir, './'.

## Overview

Tool to manage wireguard configs for server and users.
It also guarantees that server and user configs are kept properly synchronized.  
Handles key creation whenever needed, such as adding user/profile or doing key 
rollover.

Key features:

 - simplifies wireguard administration. ( server and users )
 - guarantees server and user configs remain synchronized.
 - handles key creation when needed
 - users can have multiple profiles (bob:laptop bob:phone etc)
 - users and/or profiles can be marked active/inactive 
 - takes output of 'wg show' and shows connections by user/profile name.  
   (This one solves a minor annoyance for me)
 - can import existing user/profiles

Wireguard server and user configs share several common variables, such as public keys, 
hostname and listening ports, and therefore it's crucial they are consistent.

wg-tool uses a single source of data which is used to populate the actual 
configs wireguard needs; this approach  guarantees they are always consistent
with one another. It also simplifies managment significantly. Common tasks are
handled by the tool in a convenient way. For example, It is very 
straightforward to add users or user profiles, roll keys or make users or profiles
active or inactive.

Using *wg show* on the wireguard server shows any (known) connected users
identified by their ip address and their public key. You can use the
*-rpt* option to parse that output and provide the associated
user and profile names.  It also indicates whether the user and the profile
are marked active (by showing (+) or (-) beside the name. If an inactive user 
is connected, it may be time ensure the server is running the latest wg0.config.

By convention the config files for wireguard itself will be referred to as wg-configs. These
are the outputs of *wg-tool*. We refer to the configuration 
files for wg-tool itself simply as *configs*. Directory structure for 
all the configuration files follow this simple rule.  

Specifically, the wireguard server config file, wg0.conf, will be located 
in *wg-configs/server/wg0.conf*. All the user QR codes and '.conf' files will be 
under *wg-configs/users/*

Laying out this directory structure in a bit more detail:

 - *wg-tool* configs (our inputs):

        configs/
                 server/
                     server.conf
                 users/
                     user-1/
                         user-1.conf
                     user-2/
                         user-2.conf
                     ... 

 - *wireguard* configs (our outputs):

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
                    

Each file is a symlink to an actual file kept under a *db* directory at the same level as 
the sylinks. This allows us to keep history as far back as we choose. There are options
to choose sepately the amount of history to keep for configs and wg-configs. The default
values are 5 and 3 respectively in addition to current values.

Whenever a file is changed, for convenience, the previous version of each is kept 
and named *xxx.prev*. This allows for easy comparisons and makes it easy
to revert if that were ever needed; though it should be pretty unlikely to be ever be
the case. 

On the output side each user can have multiple profiles - each profile is a separate
access to the vpn. As an example, user *jane* may have a *phone* profile and 
a *laptop* profile. Each profile will provide
a wireguard .conf file along with an image file of its QR code. These 2 files provide the 
standard wireguard configs users use.

Aside from the QR image files, all the text files are in standard TOML format.

## Getting Started

There are 2 ways to get started; either create a new suite of users/profiles or 
import existing wireguard user.conf files.  You can add users or new profiles for existing users
at any time. This is very easy and explained below using the *--add-user* option.

If you already have wireguard running then importing is the simplest and best way to proceed.
If you're starting from scratch then wg-tool will create new users and profiles for you.

Either way it's should be pretty straightforward.

### Step 1 - create server config

In either case the first step is to create a valid server config file.
The best way to do that is to run:

        wg-tool --init

This creates a template in : *configs/server/server.conf*.

This file must be edited and changed to reflect your own network settings etc.
These are all wireguard standard fields, The key fields to edit are:

 - Address
   This is the internal wg cidr mask on the server IP address 
 - Hostname and ListenPort
   wg server hostname as seen from internet and port chosen 
 - Hostname_Int ListenPort_Int
   wg server hostname and port as seen on internal network.   
   Useful for testing wg while inside the network.
 - PrivateKey, PublicKey
   If you have exsiting wg server, change these to your current keys.  
   If not they are freshly generated by --init. and can be safely used.
 - PostUp PostDown
   If you want to use the nftables provided by wg-tool - just copy postup.nft from the scripts directory.
   Change the 3 network variables at top for your setup.
 - DNS 
   List of dns servers to be used by wg - typical VPN setup uses internal network DNS 

The nftables sample script, scripts/postup.nft, should be copied to 
/etc/wireguard/scripts.

Again, remember to edit the network variables at the top of the script to match your network.
In my case,  I want to provide users with access to internet as well as internal network. So the 
system firewall forwards vpn traffic to the wireguard server which runs on the inside. 
This script provides access to internet and lan as long as the wireguard server host that access.
If your wg server is in the DMZ then it probably only has access to DMS net and internet. 

Edit the 3 variables at the top of postup.nft for your own server.

 - vpn_net
   this cidr block must match whats in the server config
 - lan_ip lan_iface
   IP and interface of wireguard server

The list of active users is managed in this server.conf file.
This is generated and updated automatically. The tool provides options to add and remove
users from the active list. If a user is inactive, none of their profiles will be in server
wg0.conf. If a user is active then only their active profiles will be provided to wg0.conf

Each user config has its own list active profiles.  It too is managed by the tool. 
N.B. the active users and active profiles lists, only affect whether they are included
in the seerver wg0.conf file. Nothing else. No user or profile is removed when a user and/or profile
is inactive.

### Step 2 - import and/or add users and profiles

Now that the server config is ready, we can add users and their profiles.

Each user can have 1 or more profiles.  wg-tool keeps user data it manages
in a single file, which holds all the users profiles. 
It also has a list of currently active profiles.

If a profile is active, it will be put in wireguards wg0.conf server config,
otherwise it won't

Wireguard QR codes and .conf files are always created for every user/profile
regardless whether it is active or not.

Each user has their own namespace, so profile names can be same for different users.

### Adding new users and profiles.

Users and profiles can be created at any time. They can be created in bulk 
or one user at a time. For example this command:

        wg-tool --add-user bob:phone,desk,ipad jane:phone,laptop

creates 2 users. *bob* gets 3 profiles : phone, desk and ipad while 
*jane* gets 2 profiles: phone and laptop.

If you don't provide a profile name, the default profile *main* will be used.

At this point you should now have server config supporting these 5 user profiles
and the corresponding wireguard QR codes and .conf files under wg-configs/users

You can get list of all users and their profiles :

        wg-tool --list_users

The (+) or (-) after a user or profile name indicates active or inactive.

### Importing existing users and profiles

The tool can import 1 user:profile at a time. This is done using:

        wg-tool --import_user \<user.conf\> user_name:profile_name

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

As above you may want to see a list of users/profiles:

        wg-tool --list_users

And compare a user profile conf or 2 with existing ones - QR codes will be different, but contain the
same informateion. You can check this for bob's laptop QR by doing this:

    zbarimg wg-configs/users/bob/bob-laptop-qr.png

which is available in the zbar package. It should match the corresponding user.conf file 
in *wg-configs/users/bob/bob-laptop.conf*


## Managing Server and Users/Profiles : Making Changes

I recommend avoiding manually editing the TOML input files, but if you do for some reason, 
then run wg-tool - it should detect your changes and update *wg-configs*.

Pretty much everything you may need to do should be available using wg-tool.

        wg-tool --help

gives list of options.


### Options

Many options take user/profiles as additional input. 
users/profiles are to be given on command line :

    user
or
    user:prof
oe
    user_1:prof_1,prof_2 user2 user_3:laptop,tablet

Thatis a summary of available options.

        positional arguments:
        users                user_1[:prof1,prof2,...] user_2[:prof_1,prof_2]

        options:
        -h 
        --help               Show this help message and exit

        -i 
        --init               Initialize - make server config template - please edit

        -add
        --add_users          Add user(s) and/or user profiles user:prof1,prof2,...

        -int
        --int_serv           With --add_users uses internal wireguard server

        -uuk
        --upd_user_keys      Update existing user(s) keys.

        -usk
        --upd_serv_keys      Update server keys - affects all users

        -all 
        --all_users          Some opts (e.g. upd_user_keys) may apply to all users/profiles

        -act 
        --active             Mark users/profiles user[:profile,...] active

        -inact 
        --inactive           Mark users/profiles user[:profile,...] inactive

        -imp <file> 
        --import_user <file> Import a wg user conf into user_name:profile_name

        -keep <num>
        --keep_hist <num>    Keep config history (default 5)

        -keep_wg <num>
        --keep_hist_wg <num> Keep wg-config history (default 3)

        -rpt <file> 
        --show_rpt <file>    Output of "wg show" -> connected users report
                             Reads file (or stdin if name is stdin")

        -l
        --list_users         List users/profiles

        -sop
        --save_opts          Set default values of keep_hist/keep_hist_wg
                             Use together with --keep_hist, --keep_hist_wg

        -v
        --verb               Be more verbose


## Key Rollover

wg-tool makes key rollover particularly simple - at least as far as updating keys
and regenerating user and/or server configs with the new keys. Its equally 
simple to update keys on a per user basis as well - just specify them on
command line. 

To roll the server keys run:

        wg-tool --upd_serv_keys

This will naturally update all user profiles with the new server public key.

To roll all user keys run:

        wg-tool --upd_user_keys

or as usual you can specify which profiles to generate the new keys for.

        wg-tool --upd_user_keys  [user:prof1,prof2 user2 ..]

As per usual, a change to any user profiles will generate a corresponding new server wg0.conf file


Distribution of the updated config/QR code to each user is not addressed by the tool.
Continue to use existing methods - encyrpted email, in person display of QR code etc. ...

## License

`wg_tool` was created by Gene C. It is licensed under the terms of the MIT license.



    

