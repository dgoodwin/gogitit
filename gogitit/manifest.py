"""Parses the gogitit manifest."""

import os
import glob
import shutil
import string
import sys

import click
import git
import yaml


# These exit status codes represent the various reasons why check may fail,
# indicating that a sync is required.
CHECK_STATUS_NO_STATUS_FILE = 1
CHECK_STATUS_MANIFEST_CHANGED = 2  # manifest checksum changed
CHECK_STATUS_SHA_CHANGED = 3  # if branch SHA1 has changed
# TODO: separate code for files not in status? status that didn't match any files?


def load(f, cache_dir):
    data = yaml.safe_load(f)
    # TODO: validation
    m = Manifest(f.name, cache_dir, **data)
    return m


def repo_url_to_dir(repo_url):
    """
    Convert a repo URL into a safe relative path we can use in our cache directory.
    """
    # drop https:// and file:// prefixes:
    path = repo_url
    if '://' in path:
        path = path.split('://')[1]

    # drop trailing and leading slashes:
    if path.startswith('/'):
        path = path[1:]
    if path.endswith('/'):
        path = path[:-1]

    # drop trailing.git suffix from repo name:
    if path.endswith('.git'):
        path = path[:-4]

    # drop username@ syntax:
    if '@' in path:
        path = path.split('@')[1]

    # replace : with /:
    path = string.replace(path, ':', '/')

    return path


class Manifest(object):
    def __init__(self, path, cache_dir, **kwargs):
        self.path = path
        self.cache_dir = cache_dir
        self.output_dir = kwargs.get('output_dir', None)
        self.repos = []
        for r in kwargs['repos']:
            self.repos.append(Repo(self, cache_dir, **r))


class Repo(object):

    def __init__(self, manifest, cache_dir, **kwargs):
        self.manifest = manifest
        self.cache_dir = cache_dir

        self.url = kwargs['url']
        self.version = kwargs.get('version', 'master')

        # Location where we maintain a git clone of this repo:
        self.repo_dir = os.path.join(self.cache_dir, repo_url_to_dir(self.url))

        self.copy = []
        for t in kwargs['copy']:
            self.copy.append(Copy(self, **t))

    def __str__(self):
        return "Repo<url=%s version=%s>" % (self.url, self.version)

    def clone(self):
        if not os.path.exists(self.repo_dir):
            click.echo("  Creating repo cache: %s" % self.repo_dir)
            os.makedirs(self.repo_dir)
            git_repo = git.Repo.clone_from(self.url, self.repo_dir)
        else:
            click.echo("  Re-using repo cache: %s" % self.repo_dir)

        git_repo = git.Repo(self.repo_dir)
        click.echo("  Fetching remotes.")
        git_repo.remotes.origin.fetch()

        if self.version in git_repo.remotes.origin.refs:
            click.echo("  Checking out branch: %s" % self.version)
            g = git_repo.git
            g.checkout("origin/%s" % self.version)

        else:
            click.echo("  Checking out ref: %s" % self.version)
            raw_repo = git.Git(self.repo_dir)
            raw_repo.checkout(self.version)

        self.sha = git_repo.head.commit.hexsha
        click.echo("  Sync commit: %s" % self.sha)

    # Alias __repr__ to __str__
    __repr__ = __str__


class Copy(object):

    def __init__(self, repo, **kwargs):
        self.repo = repo
        self.src = kwargs['src']
        self.dst = kwargs['dst']

        # Will contain globbed files and directories we intend to copy over.
        self.files_matched = []

    def __str__(self):
        return "Copy<src=%s dst=%s>" % (self.src, self.dst)

    def validate(self):
        source = os.path.join(self.repo.repo_dir, self.src)
        # mode is unused
        # mode = None
        self.files_matched = glob.glob(source)
        if len(self.files_matched) == 0 and not os.path.exists(source):
            raise click.ClickException("src does not exist in repo: %s" % source)

    def sha_check(self, status):
        copy_to_dir = self.repo.manifest.output_dir
        if self.dst:
            copy_to_dir = os.path.join(self.repo.manifest.output_dir, self.dst)

        copy_pairs = self._build_copy_pairs(copy_to_dir)
        for src, dest in copy_pairs:
            if dest not in status['paths']:
                click.echo("%s missing in status, sync is required." % dest)
                # TODO: should not sys.exit in here
                sys.exit(CHECK_STATUS_SHA_CHANGED)
            if self.repo.sha != status['paths'][dest]:
                click.echo("Commit changed for repo %s, sync is required." % self.repo.url)
                sys.exit(CHECK_STATUS_SHA_CHANGED)

    def _build_copy_pairs(self, copy_to_dir):
        """ Return list of tuples matching source path to full destination path. """
        copy_pairs = []
        for match in self.files_matched:
            # When copying a directory without a glob we require you to specify the exact
            # destination with directory name to copy as. If however you use a glob which matches
            # to a directory, we need to copy to an exact dir of dst + your globbed dir name.
            full_dest_dir = copy_to_dir
            if match != os.path.join(self.repo.repo_dir, self.src) and os.path.isdir(match):
                full_dest_dir = os.path.join(copy_to_dir, os.path.basename(match))
            copy_pairs.append((match, full_dest_dir))
        return copy_pairs

    def pre(self):
        """ Run pre-copy. """
        # Watch out for dst = '' indicating top level of output dir:
        copy_to_dir = self.repo.manifest.output_dir
        if self.dst:
            copy_to_dir = os.path.join(self.repo.manifest.output_dir, self.dst)

        # Delete all destination directories (when source is also a directory) prior to starting
        # the copy. This can't be done during because it can potentially clobber other files
        # already copied into the output dir by other pairs.
        copy_pairs = self._build_copy_pairs(copy_to_dir)
        for pair in copy_pairs:
            if os.path.isdir(pair[0]):
                # TODO: this can blow away things you've already copied into the dir, i.e. when copying a bunch of roles to 'roles':
                # If copying a dir, cleanup the target dir to remove old files:
                full_dest_dir = pair[1]
                click.echo("Pre: %s" % full_dest_dir)
                if os.path.exists(full_dest_dir):
                    click.echo("Deleting previous contents of: %s" % full_dest_dir)
                    shutil.rmtree(full_dest_dir)

    def run(self, status):
        """ Copy all files to output dir. """
        # Watch out for dst = '' indicating top level of output dir:
        copy_to_dir = self.repo.manifest.output_dir
        if self.dst:
            copy_to_dir = os.path.join(self.repo.manifest.output_dir, self.dst)

        # List of tuples, source file or path, dest path:
        copy_pairs = self._build_copy_pairs(copy_to_dir)
        for pair in copy_pairs:
            if os.path.isdir(pair[0]):
                # TODO: this can blow away things you've already copied into the dir, i.e. when copying a bunch of roles to 'roles':
                # If copying a dir, cleanup the target dir to remove old files:
                full_dest_dir = pair[1]
                click.echo("Copy:")
                click.echo("  Src: %s" % pair[0])
                click.echo("  Dest: %s" % full_dest_dir)

                shutil.copytree(pair[0], full_dest_dir, symlinks=True, ignore=shutil.ignore_patterns('.git'))
                click.echo("  Done.")
            else:
                # Make sure directory exists for the file copy:
                if pair[1][-1] == '/' and not os.path.exists(pair[1]):
                    os.makedirs(pair[1])
                elif not os.path.exists(os.path.dirname(pair[1])):
                    os.makedirs(os.path.dirname(pair[1]))

                click.echo("Copy:")
                click.echo("  Src: %s" % pair[0])
                click.echo("  Dest: %s" % pair[1])
                shutil.copy2(pair[0], pair[1])
                click.echo("  Done.")

            if 'paths' not in status:
                status['paths'] = {}
            status['paths'][pair[1]] = self.repo.sha

    # Alias __repr__ to __str__
    __repr__ = __str__
