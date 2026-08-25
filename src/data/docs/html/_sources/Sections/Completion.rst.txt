
.. _Completion:

Command Line Bash Completion
============================

Bash shell completion for options is available. It should work similarly for zsh.

To use option completion you need:

* python-argcomplete package installed
* shell program completion enabled. 
* to source output of a script to register the command line completion


python-argcomplete
------------------

Install the argcomplete pythong package. On Arch, as usual do:

.. code-block:: bash

   pacman -Syu --needed python-argcomplete


bash program completion
-----------------------

It is likely active unless you disabled it with *shopt -u progcomp*.
You can turn it on when needed or in ~/.bashrc with

.. code-block:: bash

   shopt -s progcomp

Register wg-tool completion
---------------------------

You can add this to your *.bashrc* or for testing purposes simply run
it in a terminal:

.. code-block:: bash

   eval "$(register-python-argcomplete wg-tool)"


Using Completion
----------------

Now you when you start typing an option simply press the *TAB* key to get the 
completions.

For example, with 

.. code-block:: bash

    wg-tool --<TAB>

It should display the available options. Or 

.. code-block:: bash

    wg-tool --nets<TAB>

Will list options beginning with *--nets*


