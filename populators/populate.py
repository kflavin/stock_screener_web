import click
from populators.companies import get_company_details
from populators.external.sectors import get_sector_and_industry
from populators.sectors import get_sectors_and_industries
from populators.indicators import get_ratio_data


@click.group()
@click.option('--debug', default=False, is_flag=True, help='Enable debugging.')
def start(debug):
    pass


@click.command()
@click.option('--no-throttle', default=True, is_flag=True, help='Throttle connection')
@click.option('--count', default=0, help='Number of companies to retrieve')
@click.option('--exchange', default="NYSE", help='Exchange NYSE|NASDAQ')
def companies(no_throttle, count, exchange):
    click.echo('Retrieving Companies, settings: {} {} {}'.format(no_throttle, count, exchange))
    get_company_details(no_throttle, count, exchange)


@click.command()
@click.option('--count', default=None, help='Per page number to retrieve')
def indicators(count):
    click.echo('indicators')
    get_ratio_data(count)


@click.command()
@click.option('--symbol', default=None, help='Symbol for single company')
@click.option('--count', default=None, help='Per page number to retrieve')
def sectors(symbol, count):
    click.echo('sectors')
    if symbol:
        click.echo("get company {}".format(symbol))
        # If we have a single symbol, just make the external call directly, rather than through our populator
        print get_sector_and_industry(symbol)
    else:
        get_sectors_and_industries(count)


start.add_command(companies)
start.add_command(indicators)
start.add_command(sectors)

if __name__ == '__main__':
    start()
