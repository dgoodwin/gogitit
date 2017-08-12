import click
import gogitit.manifest
import gogitit.clone
import os

@click.group()
def main():
    pass

@click.command()
@click.option('--manifest', '-m', default='manifest.yml', type=click.File('r'),
        help="Location of manifest that defines what to fetch and sync.")
@click.option('--cache-dir', default=os.path.expanduser('~/.gogitit/cache'),
        type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True),
        help="Directory where gogitit will store cached copies of repositories.")
def sync(manifest, cache_dir):
    """Fetch all remote sources and assemble into the destination directory."""
    click.echo("Executing sync")
    m = gogitit.manifest.load(manifest)
    click.echo(m.repos[0])
    for t in m.repos[0].transfers:
        click.echo("- %s" % t)

    # Make sure the working directory exists:
    if not os.path.exists(cache_dir):
        click.echo("Creating gogitit cache directory: %s" % cache_dir)
        os.makedirs(cache_dir)

    # Clone/update all repos:
    for r in m.repos:
        cloner = gogitit.clone.GitCloner(cache_dir, r)
        cloner.clone()

@click.command()
def check():
    """Scan the destination directory and it's cache and check if contents match current manifest."""
    click.echo("Checking destination directory.")

main.add_command(sync)
main.add_command(check)

if __name__ == '__main__':
    main()

