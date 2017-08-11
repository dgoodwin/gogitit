import click
import gogitit.manifest

@click.group()
def main():
    pass

@click.command()
@click.option('--manifest', '-m', default='manifest.yml', type=click.File('r'))
def sync(manifest):
    """Fetch all remote sources and assemble into the destination directory."""
    click.echo("Executing sync")
    gogitit.manifest.load(manifest)

@click.command()
def check():
    """Scan the destination directory and it's cache and check if contents match current manifest."""
    click.echo("Checking destination directory.")

main.add_command(sync)
main.add_command(check)

if __name__ == '__main__':
    main()

