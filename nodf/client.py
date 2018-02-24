#!/usr/bin/env python

#
# ** The MIT License **
#
# Copyright (c) 2013 Andrei Gherzan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Home: https://github.com/agherzan/nodf
#
# Author: Andrei Gherzan <andrei@gherzan.ro>
#

# Default variables
REPOSITORYPATH = '~/dotfiles'
BACKUPEXT = 'bak'
HOME = '~'

try:
    import os
    import git
    import argparse
    import sys
    import difflib
    import time
    from argparse import ArgumentParser
    import logging

    from .colorlogging import ColoredFormatter
    from .nodfmeta import *
except:
    print("ERROR : Can't load at least one module. Please follow README first.")
    sys.exit(1)

def getInput(valids = [], log = None):
    '''
    Function used to get user input which must be one of the ones in 'valids'.
    Return
        * user input.
    '''
    if not valids:
        return
    sys.stdout.write("Selection: ")
    s = input()
    while not s in valids:
        s = input("Wrong selection [" + '|'.join(valids)  + "]: ")
    return s

def ResolveConflict(source, destination, args, log):
    '''
    Resolve conflict between 2 files interactively

    Return
        * False if file1 should not be copied over file2
          Ex.: If user requested or errors were encountered.
        * True if file should be copied over file2.
    '''
    # If both files are the same no need to do anything
    if os.path.realpath(destination) == os.path.realpath(source):
        log.debug('%s already symlinked.' % source)
        return False

    log.warning('Conflict %s already exists.' % source)
    log.warning('[A]bort [S]kip [D]iff [F]ix Fix[B]utBackup ? ')

    # Diff option
    selection = getInput(['A', 'S', 'D', 'F', 'B'], log)
    while selection == 'D':
        sourcelines = open(source, 'U').readlines()
        destinationlines = open(destination, 'U').readlines()
        diff = difflib.ndiff(sourcelines, destinationlines)
        sys.stdout.writelines(diff)
        selection = getInput(['A', 'S', 'D', 'F', 'B'], log)

    # Other options
    if selection == 'A':
        # TODO - this is an ugly exit
        sys.exit(0)
    elif selection == 'S':
        return False
    elif selection == 'F':
        try:
            if not args.dryrun:
                os.remove(destination)
        except:
            log.error("Can't remove %s .")
            return False
    elif selection == 'B':
        try:
            if not args.dryrun:
                os.rename(destination, destination + '.' + args.backupext)
        except:
            log.error("Can't rename %s to %s.%s .", destination, destination, args.backupext)
            return False

    return True

def RepoExists(path):
    '''
    Check if a path contains a repository
    '''
    # Easiest way would be to check if path contains .git directory
    # This is not the safest way to do it but I think it should be ok for our
    # use case.
    if os.path.isdir(path + '/.git'):
        return True
    return False

def clonefunc(args, log):
    '''
    Command clones a repository in 'args.repopath'
    This path can be configured at runtime or defaults to REPOSITORYPATH.

    Return:
        * True if function succeeded
        * False if function failed
    '''
    log.info("git clone %s in %s ." %(args.repository, args.repopath))
    if RepoExists(args.repopath):
        log.warning("There is already a repository in %s ." % args.repopath)
        # This is not actually an error as maybe there is already the corect
        # repository
        return True
    if not args.dryrun:
        if not os.path.isdir(args.repopath):
            try:
                os.makedirs(args.repopath)
            except:
                log.error("The path %s doesn't exist and cannot be created." % args.repopath)
                return False
        try:
            git.cmd.Git(args.repopath).clone(args.repository, args.repopath)
        except Exception as e:
            log.error("Can't clone in %s." % args.repopath)
            return False
    return True

def pullfunc(args, log):
    '''
    Pull repository for remote changes
    Ex.: have the same repository on multiple machines.

    Return:
        * True if function succeeded
        * False if function failed
    '''
    log.info("git pull in %s ." % args.repopath)
    if not RepoExists(args.repopath):
        log.error("There is no %s repository." % args.repopath)
        return False
    if not args.dryrun:
        try:
            git.cmd.Git(args.repopath).pull()
        except:
            log.error("Can't pull in %s ." % args.repopath)
            return False
    else:
        log.debug("Not actually pulling, just dry run.")
    return True

def listfunc(args, log):
    '''
    List origin remote in the repository

    Return:
        * True if function succeeded
        * False if function failed
    '''
    log.info("Getting origin remote from %s ." % args.repopath)
    try:
        g = git.cmd.Git(args.repopath)
        remote = g.config('remote.origin.url')
    except:
        log.warn("No origin remote found in %s repository." % args.repopath)
        return False
    log.info("%s cloned from [%s]." % (args.repopath, remote))
    return True

def statusfunc(args, log):
    '''
    Git status in the repository

    Return:
        * True if function succeeded
        * False if function failed
    '''
    log.info("Checking repository status in %s ." % args.repopath)
    if not RepoExists(args.repopath):
        log.error("There is no %s repository." % args.repopath)
        return False
    g = git.cmd.Git(args.repopath)
    log.info("%s" % g.status())
    return True

def trackfunc(args, log):
    '''
    Track one or more files in repository
    Copy all files in repository and create symlinks in their old location

    Return:
        * True if function succeeded
        * False if function failed
    '''
    for file in args.files:
        log.info('Tracking %s in %s.' %(file, args.repopath))

        # Arbsolute and clean path to file
        file = os.path.abspath(os.path.normpath(file))

        if not os.path.isfile(file):
            log.warn("File %s does not exist." % file)
            continue

        repofile = args.repopath + '/' + os.path.relpath(file, args.home)
        repofile = os.path.abspath(os.path.normpath(repofile))

        if not args.home in repofile:
            log.warn("File %s not in home directory." % file)
            continue

        if os.path.exists(repofile):
            if ResolveConflict(file, repofile, args, log) == False:
                continue

        if not args.dryrun:
            try:
                os.renames(file, repofile)
                if not os.path.exists(os.path.dirname(file)):
                    os.makedirs(os.path.dirname(file))
                os.symlink(repofile, file)
            except:
                log.warn("Can't track %s ." % (file))
                continue
    return True

def symlinkfunc(args, log):
    '''
    Go through all files in repo and create corespondent symlinks in path

    Return:
        * True if function succeeded
        * False if function failed
    '''
    log.debug("Symlink command on %s repository." % args.repopath)

    if not RepoExists(args.repopath):
        log.error("There is no %s repository." % args.repopath)
        return False

    for root, dirs, files in os.walk(args.repopath):
        # Don't go in .git - obviously
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            log.info('Symlinking %s .' % file)
            repofile = root + '/' + file
            symlinkfile = args.home + '/' + os.path.relpath(repofile, args.repopath)
            log.debug('Symlinking %s -> %s.' % (repofile, symlinkfile))
            if os.path.exists(symlinkfile):
                if ResolveConflict(repofile, symlinkfile, args, log) == False:
                    continue
            if not os.path.exists(os.path.dirname(symlinkfile)):
                if not args.dryrun:
                    try:
                        os.makedirs(os.path.dirname(symlinkfile))
                    except:
                        log.error("Can't create symlink in %s ." % symlinkfile)
                        continue
            if not args.dryrun:
                try:
                    os.symlink(repofile, symlinkfile)
                except:
                    log.error("Can't create symlink in %s ." % symlinkfile)
    return True

def initfunc(args, log):
    '''
    Initialize repository in args.repopath

    Return:
        * True if function succeeded
        * False if function failed
    '''
    log.info("Initializing repository in %s ." % args.repopath)

    if os.path.exists(args.repopath):
        if os.listdir(args.repopath):
            log.error("Repository path %s already exists and is not empty." % args.repopath)
            return False
    else:
        if not args.dryrun:
            os.mkdir(args.repopath)
    try:
        if not args.dryrun:
            g = git.cmd.Git(args.repopath).init()
    except:
        log.error("Can't initialize repository in %s ." % args.repopath)

def main():
    '''
    Main
    '''
    # Parse arguments
    parser = ArgumentParser(add_help=False, description=description)
    parser.add_argument('-v', '--version', action='version', version=version)
    parser.add_argument('-h', '--help', action='help',
                      help = 'Print this message and exit')
    parser.add_argument('-d', '--debug', action="store_true", dest = 'debug', default = False,
                      help = 'Run in debug/verbose mode')
    parser.add_argument('-r', '--repo', default = REPOSITORYPATH, dest = 'repopath',
                      help = 'Repository path to be used. Default: ' + REPOSITORYPATH)
    parser.add_argument('--dry-run', action = 'store_true', dest = 'dryrun', default = False,
                      help = "Don't actually run commands")
    parser.add_argument('-n', '--no-colors', action = 'store_false', dest = 'colors', default = True,
                      help = "Don't use any colors")
    # Commands
    subparsers = parser.add_subparsers(title = 'Commands',
        description = 'Commands to manipulate files. \
                       Run "nodf <comand> -h" to see help for each command.')
    clone = subparsers.add_parser('clone', help='Clone repository')
    clone.add_argument('repository', help='Repository to be cloned')
    clone.set_defaults(func=clonefunc)
    pull = subparsers.add_parser('pull', help='Pull repository')
    pull.set_defaults(func=pullfunc)
    list = subparsers.add_parser('list', help='List origin remote in repository')
    list.set_defaults(func=listfunc)
    status = subparsers.add_parser('status', help='Check repository status')
    status.set_defaults(func=statusfunc)
    track = subparsers.add_parser('track', help='Track files')
    track.add_argument('files', nargs='+', help='Files to be tracked')
    track.add_argument('-b', '--backup-ext', default = BACKUPEXT, dest = 'backupext',
                      help = 'Extension to be used when backup conflicting files. Default: ' + BACKUPEXT)
    track.set_defaults(func=trackfunc)
    symlink = subparsers.add_parser('symlink', help='Symlink repository')
    symlink.add_argument('-b', '--backup-ext', default = BACKUPEXT, dest = 'backupext',
                      help = 'Extension to be used when backup conflicting files. Default: ' + BACKUPEXT)
    symlink.set_defaults(func=symlinkfunc)
    init = subparsers.add_parser('init', help='Init repository')
    init.set_defaults(func=initfunc)

    args = parser.parse_args()

    # Logger
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(ColoredFormatter(args.colors))
    log.addHandler(ch)

    # Expand paths
    args.repopath = os.path.normpath(os.path.expanduser(args.repopath))
    args.home = os.path.normpath(os.path.expanduser(HOME))

    if args.debug:
        log.setLevel(logging.DEBUG)
        log.debug("Running in debug/verbose mode.")

    if hasattr(args, 'func'):
        if not args.func(args, log):
            log.debug("Return exit code 1 as command failed.")
            sys.exit(1)

if __name__ == "__main__":
    main()
