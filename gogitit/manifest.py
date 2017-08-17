"""Parses the gogitit manifest."""

import os
import glob
import shutil

import click
import git
import yaml


def load(f, cache_dir):
    data = yaml.safe_load(f)
    # TODO: validation
    m = Manifest(cache_dir, **data)
    return m


class Manifest(object):
    def __init__(self, cache_dir, **kwargs):
        self.cache_dir = cache_dir
        self.repos = []
        for r in kwargs['repos']:
            self.repos.append(Repo(cache_dir, **r))


class Repo(object):

    def __init__(self, cache_dir, **kwargs):
        self.cache_dir = cache_dir

        # TODO: repoid must be valid for a directory name as we use it in caches:
        self.id = kwargs['id']

        self.url = kwargs['url']
        self.version = kwargs.get('version', 'master')

        # Location where we maintain a git clone of this repo:
        self.repo_dir = os.path.join(self.cache_dir, self.id)

        self.copy = []
        for t in kwargs['copy']:
            self.copy.append(Copy(self.repo_dir, **t))

    def __str__(self):
        return "Repo<id=%s url=%s version=%s>" % (self.id, self.url, self.version)

    def clone(self):
        if not os.path.exists(self.repo_dir):
            click.echo("Creating repo cache: %s" % self.repo_dir)
            os.makedirs(self.repo_dir)
            click.echo("Cloning %s" % self.url)
            git_repo = git.Repo.clone_from(self.url, self.repo_dir)
        else:
            click.echo("Re-using repo cache: %s" % self.repo_dir)

        git_repo = git.Repo(self.repo_dir)
        click.echo("Fetching remotes.")
        git_repo.remotes.origin.fetch()

        if self.version in git_repo.remotes.origin.refs:
            click.echo("Checking out branch: %s" % self.version)
            git_repo.remotes.origin.refs[self.version].checkout(force=True)
        else:
            click.echo("Checking out ref: %s" % self.version)
            raw_repo = git.Git(self.repo_dir)
            raw_repo.checkout(self.version)

    # Alias __repr__ to __str__
    __repr__ = __str__


class Copy(object):

    def __init__(self, repo_dir, **kwargs):
        self.repo_dir = repo_dir
        self.src = kwargs['src']
        self.dst = kwargs['dst']

        # Will contain globbed files and directories we intend to copy over.
        self.files_matched = []

    def __str__(self):
        return "Copy<src=%s dst=%s>" % (self.src, self.dst)

    def validate(self):
        source = os.path.join(self.repo_dir, self.src)
        click.echo("source = %s" % source)
        # mode is unused
        # mode = None
        self.files_matched = glob.glob(source)
        click.echo(self.files_matched)
        if len(self.files_matched) == 0 and not os.path.exists(source):
            raise click.ClickException("src does not exist in repo: %s" % source)

    def run(self, output_dir):
        # List of tuples, source file or path, dest path:
        copy_to_dir = os.path.join(output_dir, self.dst)
        copy_pairs = []
        for match in self.files_matched:
            copy_pairs.append((match, copy_to_dir))

        for pair in copy_pairs:
            click.echo("%s -> %s" % pair)
            if os.path.isdir(pair[0]):
                # If copying a dir, cleanup the target dir. Appending a / here if it's
                # a directory as not doing so causes bugs with copying the source dir name
                # into a nested dir of the same name.
                full_dest_dir = os.path.abspath(os.path.join(
                    copy_to_dir,
                    os.path.basename(pair[0] + "/")))
                if os.path.exists(full_dest_dir):
                    click.echo("Deleting old contents of: %s" % full_dest_dir)
                    shutil.rmtree(full_dest_dir)
                click.echo("copying tree")
                shutil.copytree(pair[0], pair[1], symlinks=True)
                click.echo("copy completed")
            else:
                # Make sure directory exists for the file copy:
                dest_dir = os.path.dirname(os.path.abspath(pair[1]))
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                shutil.copy2(pair[0], pair[1])

    # Alias __repr__ to __str__
    __repr__ = __str__
