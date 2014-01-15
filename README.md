##Table of Contents##
- [A. Description](#a-description)
- [B. Installation](#b-installation)
- [C. How To Use](#c-how-to-use)


A. Description
==============

A tool to be used for managing and storing dotfiles but coded to be able
to accomodate any kind of files

B. Installation
===============

    $ cd <nodf git clone directory>
    $ sudo ./setup.py install


C. How To Use
=============

Basically all fuctions should be clearly described in help: running nodf -h.

To clone a repository run in the default location (which is ~/dotfiles):

    $ nodf clone <repo url>

If you don't have a dotfiles repository and want just to initialize a new git:

    $ nodf init

After cloning the repository, you can create symlinks for all files in dotfiles
repository using:

    $ nodf symlink

Note that all files in dotfiles should be relative to home directory. So, for a file in
~/dotfile/tmp/file, this will create a symlink in ~/tmp/file.

To track a new (or some) file:

    $ nodf track file1 file2

This will actually move these files in dotfiles repository and create symlinks in their
old location. You will probebly want to add/commit/push in dotfiles repository after
this. Again, all files should be located in your HOME directory. Obviusly it doesn't
matter if these files are actually dotfiles.

To list the remote used as dotfiles repository:

    $ nodf list

To check status of remote dotfiles repository:

    $ nodf status
