##Table of Contents##
- [A. Description](#a-description)
- [B. Installation](#b-installation)
    - [B.1. Prerequisites](#b1-prerequisites)
    - [B.2. Install](#b2-install)
- [C. How To Use](#c-how-to-use)


A. Description
==============


B. Installation
===============

B.1. Prerequisites
------------------
Have python and other prerequisites on host:

* python
* GitPython

Example - Fedora:

    $ sudo yum install python GitPython

Example - Ubuntu:

    $ sudo apt-get install python GitPython

B.2. Install
------------
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
