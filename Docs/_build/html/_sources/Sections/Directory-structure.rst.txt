Directory and File Structure
============================

*wg-tool* uses files to hold all it's data.
It uses 3 directories, one for it's own data, one for the
wireguard config output and one for edits to existing data.

* *Data*

  This holds all the tool's own data.
  Every vpn, account and profile data reside under this.

* *Data-wg*

  The wireguard configs, which are the final output, are all under this.

* *Edits*

  This is used whenever any item is modifed. The *--edit* option saves a file
  here, which can be modified and merged back (*--merge*). It's just a temporary
  working area used while making any changes.


Tool Database and Wireguard Configs
-----------------------------------

Each individual item uses an identifier that is made of 3 parts: 

.. code-block:: none

    vpn-name . peer-name . profile-name, 
    
and the directory structure for both *Data* and *Data-wg* follows this hierarchy. 

All the wireguard configs are saved in *Data-wg*. This includes any
QR codes for client profiles which are in it's *qr*
sub-directory.

.. code-block:: none

    Data/
        <vpn-name>/
            <account-name-1>/
                        <profle-name-1>.prof
                        <profle-name-1>.prof
                    
            <account-name-2>/
                        <profle-name-1>.prof
                        <profle-name-1>.prof

.. code-block:: none

    Data-wg/
        <vpn-name>/
            <account-name-1>/
                <profle-name-1>.conf
                <profle-name-1>.conf
                        qr/
                            <profile-name-1>.png
                            <profile-name-2>.png
            <account-name-2>/
                <profle-name-1>.conf
                <profle-name-1>.conf


For both Data and Data-wg files, each file is a symlink to a file which resides under
the *_.db._* subdirectory. This permits keeping some history on each file. The number of
history files kept is an available option. There are separate options for Data and Data-wg.

For example:

.. code-block:: none

    <some directory>
                laptop.prof -> _.db._/<date-1>/laptop.prof

                _.db._/
                    <date-1>/laptop.prof
                    <date-2>/laptop.prof
                    ...
                    



When *wg-tool --edit <ID>* is used it displays the edit file path. Changes to that file
can be merged back with the *--merge* option.

All edit files fall under the *Edits* directory:

.. code-block:: none

   Edits/
        <vpn-name>-info.mods
        <vpn-name>:<account-name>:<profile-name>.mods

