import sys
import click

from pipeline import expand_abbreviation, abbreviate_journal_name
from train_ngram_models import retrain_bigrams
from train_freq_models import retrain_freq_models
from test_sample import print_sample_test, output_sample_test_csv

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


@main.command()
@click.argument('retrain', required = False)
def retrain(**kwargs):
    """Re-train the bigram models and frequency counts """
    retrain_bigrams()
    retrain_freq_models()
    # click.echo(result)

@main.command()
@click.argument('printtest', required = False)
def printtest(**kwargs):
    """Test a sample and print it"""
    print_sample_test()

@main.command()
@click.argument('csvtest', required = False)
def csvtest(**kwargs):
    """Test a sample and print it"""
    output_sample_test_csv()



if __name__ == '__main__':
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("ISO4 deabbreviator -- Expand Abbreviated Journal Names")
    main()