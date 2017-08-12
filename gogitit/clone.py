"""Objects for cloning remote repositories. (typically git)"""

import click
import os
import git

class GitCloner(object):
    def __init__(self, cache_dir, repo):
        self.cache_dir = cache_dir
        self.repo = repo

    def clone(self):
        clone_dir = os.path.join(self.cache_dir, self.repo.id)

        click.echo("Using repo cache directory: %s" % clone_dir)
        if not os.path.exists(clone_dir):
            os.makedirs(clone_dir)
            click.echo("Cloning %s..." % self.repo.url)
            git_repo = git.Repo.clone_from(self.repo.url, clone_dir)

        git_repo = git.Repo(clone_dir)
        git_repo = git.Git(clone_dir)
        click.echo("Checking out %s..." % self.repo.version)
        git_repo.checkout(self.repo.version)
