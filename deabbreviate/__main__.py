import sys
import click
from pipeline import expand_abbreviation, abbreviate_journal_name

@click.group()
@click.version_option("1.0.0")
def main():
    """A ISO4 abbreviation expansion tool"""
    pass


@main.command()
@click.argument('expand', required=False)
def expand(**kwargs):
    """Expand an abbreviated journal name"""
    result = expand_abbreviation(kwargs.get("expand"))
    click.echo(result)

@main.command()
@click.argument('abbreviate', required = False)
def abbreviate(**kwargs):
    """Abbreviate a full journal name"""
    result = abbreviate_journal_name(kwargs.get("abbreviate"))
    click.echo(result)

if __name__ == '__main__':
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("ISO4 deabbreviator -- Expand Abbreviated Journal Names")
    main()