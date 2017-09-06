import click
import gogitit.manifest
import hashlib
import os
import sys
import yaml

# Will be written to the top level of the output directory and tracks
# everything we wrote on last successful sync.
CACHE_FILE = ".gogitit-cache.yml"


@click.command()
@click.option(
        '--manifest-file', '-m', default='gogitit.yml', type=click.File('r'),
        help="Location of manifest that defines what to fetch and sync.")
@click.option(
        '--cache-dir', default=os.path.expanduser('~/.gogitit/cache'),
        type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True),
        help="Directory where gogitit will store cached copies of repositories.")
@click.option(
        '--output-dir', '-o', default=os.path.abspath('./'),
        type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True),
        help="Directory where all output will be assembled into final structure.")
def sync(manifest_file, cache_dir, output_dir):
    """Fetch all remote sources and assemble into the destination directory."""
    click.echo("Executing sync to output directory: %s" % output_dir)
    # Make sure the working directory exists:
    if not os.path.exists(cache_dir):
        click.echo("Creating gogitit cache directory: %s" % cache_dir)
        os.makedirs(cache_dir)

    manifest = gogitit.manifest.load(manifest_file, cache_dir)
    click.echo(manifest.repos[0])
    for copy in manifest.repos[0].copy:
        click.echo("- %s" % copy)

    # Clone/update all repos:
    for repo in manifest.repos:
        repo.clone()
        for copy in repo.copy:
            copy.validate()

    status = {}
    manifest_file.seek(0)
    status['manifest_sha'] = hashlib.sha1(manifest_file.read()).hexdigest()
    click.echo("Manifest SHA: %s" % status['manifest_sha'])

    for repo in manifest.repos:
        for copy in repo.copy:
            copy.run(output_dir, status)

    click.echo(status)

    # Write the cache of what we synced:
    f = open(os.path.join(output_dir, CACHE_FILE), 'w')
    f.write(yaml.dump(status))
    f.close()


@click.command()
@click.option(
        '--manifest-file', '-m', default='gogitit.yml', type=click.File('r'),
        help="Location of manifest that defines what to fetch and sync.")
@click.option(
        '--cache-dir', default=os.path.expanduser('~/.gogitit/cache'),
        type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True),
        help="Directory where gogitit will store cached copies of repositories.")
@click.option(
        '--output-dir', '-o', default=os.path.abspath('./'),
        type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True),
        help="Directory where all output will be assembled into final structure.")
def check(manifest_file, cache_dir, output_dir):
    """
    Scan the destination directory and it's cache and check if contents
    match current manifest.
    """
    click.echo("Checking if sync is required for output directory: %s" % output_dir)

    manifest = gogitit.manifest.load(manifest_file, cache_dir)
    status_filepath = os.path.join(output_dir, CACHE_FILE)
    click.echo(status_filepath)
    if not os.path.exists(status_filepath):
        click.echo("No status file exists, sync is required: %s" % status_filepath)
        sys.exit(gogitit.manifest.CHECK_STATUS_NO_STATUS_FILE)
    status = yaml.load(open(status_filepath))

    manifest_file.seek(0)
    current_manifest_sha = hashlib.sha1(manifest_file.read()).hexdigest()
    if current_manifest_sha != status['manifest_sha']:
        click.echo("Manifest has changed, sync is required.")
        sys.exit(gogitit.manifest.CHECK_STATUS_MANIFEST_CHANGED)

    # Make sure the working directory exists:
    if not os.path.exists(cache_dir):
        click.echo("Creating gogitit cache directory: %s" % cache_dir)
        os.makedirs(cache_dir)

    # Clone/update all repos:
    for repo in manifest.repos:
        repo.clone()
        for copy in repo.copy:
            copy.validate()

    # All repos in cache should now have checked out the correct SHA:
    for repo in manifest.repos:
        for copy in repo.copy:
            copy.sha_check(status, output_dir)


CACHE_FILE = '.gogitit-cache.yml'


@click.group()
def main():
    pass


main.add_command(sync)
main.add_command(check)


if __name__ == '__main__':
    main()
