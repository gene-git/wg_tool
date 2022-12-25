# wg_tool

Tool to manage wireguard configs for server and users.

## Installation

Available on 
 - [Github source ](https://github.com/gene-git/wg_tool)
 - [Archlinux AUR](https://aur.archlinux.org/packages/wg_tool)   
   PKGBUILD also in source tree under packaging

If on Arch can build using the PKGBUILD provided which is also available in the AUR.

To build it manually, clone the repo and do:

        rm -f dist/*
        poetry build --format wheel
        root_dest="/"
        ./scripts/do-install $root_dest

  If running as non-root then set root\_dest a user writable directory

### Dependencies

- Run Time :
  - python (3.9 or later)
  - wireguard-tools
  - nftables (for wireguard server postup.nft)
  - tomli\_w (aka python-tomli\_w )
  - netaddr (aka python-netaddr )
  - python-qrcode
  - If python < 3.11 : tomli (aka python-tomli)

- Building Package:
  - git
  - poetry (aka python-poetry)
  - wheel (aka python-wheel)
  - pip (aka python-pip)
  - rsync

## Interesting, New or Coming Soon

### New

   - Stronger file access permissions to protect private data in configs.

   - Changes to work_dir.
     Backward compatible with previous version.
     Now prefers to use */etc/wireguard/wg-tool* if possible, otherwise 
     falls back to current directory.

### Newish

   - *-dnsrch, --dns_search*  
     Adds the list DNS_SEARCH from server config to client DNS search list.  
     DNS_SEARCH in server.conf should contain a list of dns domains for dns search.  
     Use together with *-add* for new user:profile or with *-mod* with existing profile.

   - *-dnslin, --dns_linux*  
     For a Linux client, provide support for managing dns resolv.conf.
     i.e. Save existing, install wg dns and restore on wg exit.
     Use together with *-add* for new user:profile or with *-mod* with existing profile.
     See below or help for more detail.

### Useful: Report from running wg server shows user:profile names

   - *-rrpt*   
     Same as -rpt, but runs *wg show* for you. This obviously only works 
     when run on the vpn server. Will advise if current server is out of 
     sync with current config and therefore needs updating and/or restarting

        wg-tool -rrpt

This feature solves a long standing problem with native wireguard reports which 
burden the administrator with mapping IPs or public keys to a user profile. 
This eliminates any need for schemes, such as Vanity keys, attempting to map 
public keys to something more palatable.

    
## Overview

Tool to manage wireguard configs for server and users.

It also guarantees that server and user configs are kept properly synchronized.  
Handles key creation whenever needed, such as adding user/profile or doing key 
rollover.

In a nutshell to setup and use wireguard vpn one needs a server and each client 
gets a configuration, either in the form of a text based *.conf* file or
a QR code. QR codes work nicely for wireguard phone app, for example, where the 
app uses on board camera to read the the QR code. For computer clients, the conf file 
is the simplest. The server and client keys share common information which must be kept
synchronized. This includes shared public keys, pre-shared keys for added security
along with network information (IPs, Ports and DNS).

The tool uses a file based configuration database kept under the *config* directory.
This provides all the inputs the tool needs to generate the server and client configs.
The latter are saved into the *wg-config/server* and *wg-config/users* directories 
for server and clients respectively.

The wg server config, *wg-config/server/wg0.conf* should be installed, as usual, 
in /etc/wireguard. 

Each user can have 1 or more profiles. For example bob may have *bob:phone* and 
*bob:laptop*.  The configs to share with each profile is saved into, in this example,
*wg-config/users/bob* as bob-phone.conf, bob-phone-qr.png, bob-laptop.conf and bob-laptop-qr.png.
These are provided to the user - bob in this case.

For computer clients running Linux, there are 2 kinds of configs available. The standard config
where the DNS infomation in config is used by wg-quick. wg-quick, in turn, relies on resolvconf.

The alternative, which is definitely my preference, is to use the --dns\_linux option in which
wg-quick uses the *wg-peer-updn* script (provided here) via PostUp/PostDown. This 
saves the current dns resolv.conf file when VPN is brought up using *wg-quick up*, installs 
the VPN dns into /etc/resolv.conf and restores prior resolv.conf when VPN is 
deactivated (wg-quick down).

For convenience, previous configs are saved with *.prev* extension making it easy
to compare with a prior version. It can be useful after making changes to
diff the two configs.

Key features:

 - simplifies wireguard administration. ( server and users )
 - guarantees server and user configs remain synchronized.
 - handles key creation when needed
 - users can have multiple profiles (bob:laptop bob:phone etc)
 - users and/or profiles can be marked active/inactive 
 - takes output of 'wg show' and shows connections by user/profile name.  
   Includes check that server is up to date or may need restart with new wg0.conf
   This solves a minor annoyance in a simple way.
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
at any time. This is very easy and explained below using the *--add_user* option.
You can also import a user at any time, though it's primarily useful when first
setting up wg-tool.

If you already have wireguard running then importing is the simplest and best way to proceed.
If you're starting from scratch then wg-tool will create new users and profiles for you.

Either way it's pretty straightforward.

### Step 1 - Create Server Config

In either case the first step is to create a valid server config file.
The best way to do that is to run:

        wg-tool --init
or
        wg-tool --work_dir=xxx --init

By default, when initializing,  work_dir will be */etc/wireguard/wg-tool* if exists and if have
 appropriate access permission (i.e. root), otherwise the current directory *./*.

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

Each user can have 1 or more profiles.  wg-tool keeps each user's data 
in a single file, which holds all that users profiles. 
It also has a list of currently active profiles.

If a profile is active, it will be put in wireguards wg0.conf server config,
otherwise it won't.

Wireguard QR codes and .conf files are always created for every user/profile
regardless whether it is active or not.

Each user has their own namespace, so profile names can be same for different users.

### Adding new users and profiles.

Users and profiles can be created at any time. They can be created in bulk 
or one user at a time. For example this command:

        wg-tool --add_user bob:phone,desk,ipad jane:phone,laptop

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

Summary of available options.

        positional arguments:
        users                user_1[:prof1,prof2,...] user_2[:prof_1,prof_2]

        options:

 - *-h, --help*   
   Show this help message and exit

 - *-i, --init*   
   Initialize and creat server config template. 
   Please edit to match your server settings.

 - *wkd, --work_dir <dirname>*   
   Set working directory.  
   This is is the directory holding all configs.
   By default: 
    - when used with *--init*, work_dir will be */etc/wireguard/wg-tool* if directory exists and 
      if have appropriate access permission (i.e. root), otherwise the current directory *./*.
    - if not initializing, then, if have access permission,  */etc/wireguard/wg-tool/* will be 
      the work_dir if there is a *config* dir in it, otherwise it is set to  current dir *./*.

 - *-add, --add_users*   
   Add user(s) and/or user profiles user:prof1,prof2,...

 - *-mod, --mod_users*   
   Modify existing user:profile(s).  Use with *-dnsrch* and *-dnslin*

 - *-dnsrch, --dns_search*  
   Adds the list DNS_SEARCH from server config to client DNS search list.
   DNS_SEARCH in server.conf should contain a list of dns domains for dns search and 
   Use together with *-add* for new user:profile or with *-mod* with existing profile.

 - *-dnslin, --dns_linux*  
   For a Linux client, provide support for managing dns resolv.conf.
   i.e. Save existing, install wg dns and restore on wg exit.
   Use together with *-add* for new user:profile or with *-mod* with existing profile.

   To bring up wireguard as a linux client one uses 
   i.e. Save existing, install wg dns and restore on wg exit.

        wg-quick up \<user-prof.conf\> 
        wg-quick down \<user-prof.conf\> 

For example to add dns search and use dns_linux on existing user profile. First edit 
*configs/server/server.conf* and add list of seach domains :

        DNS_SEARCH = ['sales.example.com', 'example.com']
        wg-tool -mod -dnsrch -dns_linux bob:laptop

By default wg-quick uses resolvconf to manage dns resolv.conf.  If you prefer, or dont use resolvconf
then use this option. But only use with Linux - it will not work for other clients (Android, iOS, etc)

With this option the usual DNS rows in in the conf file are replaced with PostUp and PostDown.  
PostUp saves existing resolv.conf, and installs the one needed by wireguard.
PostDown restores the original saved resolv.conf.

To use this the script *wg-peer-updn*, available in the *scripts* directory must be
in /etc/wireguard/scripts for the client. 
The installer for the wg_tool package installs the script - but clients without this
package should be provided both the user-profile.conf as well as the supporting 
script *wg-peer-updn*. 


 - *-int, --int_serv*   
   With --add_users uses internal wireguard server

 - *-uuk, --upd_user_keys*   
   Generate new set of keys for existing user(s).
   This is public and private key pair along with new pre-shared key.

 - *-usk, --upd_serv_keys*   
   Generate new pair of server keys.
   NB This affects all users as they all use the server public key.

 - *-all, --all_users*  
   Some opts (e.g. upd_user_keys) may apply to all users/profiles when this is turned on.

 - *-act, --active*   
   Mark one or more users or user[:profile, profile...] active

 - *-inact, --inactive*    
   Mark one or more users or user[:profile, profile...] inactive

 - *-imp, --import_user <file>*    
   Import a standard wg user conf file into the spcified user_name:profile_name
   This is for one single user:profile

 - *-keep, --keep_hist <num>*   
   How much config history to keep (default 5)

 - *-keep_wg, --keep_hist_wg <num>*   
   How much wg-config history to keep (default 3)

 - *-sop, --save_opts*   
   Together with --keep_hist and/or --keep_hist_wg
   to save these values as new defaults.

 - *-rrpt, --run_show_rpt*   
   Run "wg show" and generate report of users, profiles.
   Also checks for consistency with current settings.

 - *-rpt, --show_rpt <file>*   
   Same as *-rrpt* only reads file containing the output of *wg show*
   If file is name *stdin*, then it reads from stdin.

 - *-l, --list_users*   
   Summary of users/profiles - sorted by user.

 - *-det, --details*    
   Adds more detail to *-l* and *-rrpt*.
   For *-l* report will also include details about each profile.
   For *-rrpt* report will show all user:profiles known to running server, not just
   those for which it has a recent connection. 

 - *-v, --verb*   
   Adds more verbose output.


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



## Notes

   - Config changes are tracked by modification times.  
     For existing user/profiles without a saved value of *mod\_time*, 
     the last change date-time of the config file is used and saved.
     These mod times are displayed when using *-l* and *-l -det*.


## License

`wg_tool` was created by Gene C. It is licensed under the terms of the MIT license.



    

