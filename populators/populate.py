import click
from populators.companies import get_company_details


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
def indicators():
    click.echo('indicators')


@click.command()
def sectors():
    click.echo('sectors')


start.add_command(companies)
start.add_command(indicators)
start.add_command(sectors)

if __name__ == '__main__':
    start()
