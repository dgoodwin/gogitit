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
        '--output-dir', '-o', default=None,
        type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True),
        help="Directory where all output will be assembled into final structure.")
def sync(manifest_file, cache_dir, output_dir):
    """Fetch all remote sources and assemble into the destination directory."""
    # Make sure the working directory exists:
    if not os.path.exists(cache_dir):
        click.echo("Creating gogitit cache directory: %s" % cache_dir)
        os.makedirs(cache_dir)

    manifest = gogitit.manifest.load(manifest_file, cache_dir)
    output_dir = setup_output_dir(manifest, output_dir)
    click.echo("\nSyncing to: %s" % output_dir)

    click.echo("\nCloning repositories:\n")

    # Clone/update all repos:
    for repo in manifest.repos:
        click.echo("Cloning: %s" % repo.url)
        repo.clone()
        for copy in repo.copy:
            copy.validate()

    status = {}
    manifest_file.seek(0)
    status['manifest_sha'] = hashlib.sha1(manifest_file.read()).hexdigest()

    click.echo("\nBuilding output directory:\n")

    for repo in manifest.repos:
        for copy in repo.copy:
            copy.pre()

    for repo in manifest.repos:
        for copy in repo.copy:
            copy.run(status)

    # Write the cache of what we synced:
    f = open(os.path.join(output_dir, CACHE_FILE), 'w')
    f.write(yaml.dump(status))
    f.close()

    click.echo("\nOutput ready in: %s\n" % output_dir)


def setup_output_dir(manifest, cli_output_dir):
    """ Normalize the manifest output dir with the optional CLI override. """
    if not manifest.output_dir and not cli_output_dir:
        click.echo("No output dir defined in manifest or CLI argument.")
        sys.exit(1)

    if cli_output_dir:
        manifest.output_dir = cli_output_dir
    else:
        # Make the manifest output_dir relative to manifest location if not absolute:
        if manifest.output_dir[0] != '/':
            manifest.output_dir = os.path.abspath(os.path.join(
                os.path.dirname(manifest.path), manifest.output_dir))

    return manifest.output_dir


@click.command()
@click.option(
        '--manifest-file', '-m', default='gogitit.yml', type=click.File('r'),
        help="Location of manifest that defines what to fetch and sync.")
@click.option(
        '--cache-dir', default=os.path.expanduser('~/.gogitit/cache'),
        type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True),
        help="Directory where gogitit will store cached copies of repositories.")
@click.option(
        '--output-dir', '-o', default=None,
        type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True),
        help="Directory where all output will be assembled into final structure.")
def check(manifest_file, cache_dir, output_dir):
    """
    Scan the destination directory and it's cache and check if contents
    match current manifest.
    """
    manifest = gogitit.manifest.load(manifest_file, cache_dir)
    output_dir = setup_output_dir(manifest, output_dir)
    click.echo("Checking if sync is required for output directory: %s" % output_dir)

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
            copy.sha_check(status)


CACHE_FILE = '.gogitit-cache.yml'


@click.group()
def main():
    pass


main.add_command(sync)
main.add_command(check)


if __name__ == '__main__':
    main()
