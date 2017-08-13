import click
import gogitit.manifest
import os

@click.command()
@click.option('--manifest', '-m', default='manifest.yml', type=click.File('r'),
        help="Location of manifest that defines what to fetch and sync.")
@click.option('--cache-dir', default=os.path.expanduser('~/.gogitit/cache'),
        type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True),
        help="Directory where gogitit will store cached copies of repositories.")
@click.option('--output-dir', '-o', default=os.path.abspath('./'),
        type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True),
        help="Directory where all output will be assembled into final structure.")
def sync(manifest, cache_dir, output_dir):
    """Fetch all remote sources and assemble into the destination directory."""
    click.echo("Executing sync to output directory: %s" % output_dir)
    # Make sure the working directory exists:
    if not os.path.exists(cache_dir):
        click.echo("Creating gogitit cache directory: %s" % cache_dir)
        os.makedirs(cache_dir)

    manifest = gogitit.manifest.load(manifest, cache_dir)
    click.echo(manifest.repos[0])
    for copy in manifest.repos[0].copy:
        click.echo("- %s" % copy)

    # Clone/update all repos:
    for repo in manifest.repos:
        repo.clone()
        for copy in repo.copy:
            copy.validate()

    for repo in manifest.repos:
        for copy in repo.copy:
            copy.run(output_dir)

@click.command()
def check():
    """
    Scan the destination directory and it's cache and check if contents
    match current manifest.
    """
    click.echo("Checking destination directory.")

@click.group()
def main():
    pass

main.add_command(sync)
main.add_command(check)

if __name__ == '__main__':
    main()

