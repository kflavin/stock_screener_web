import click
from populators.companies import get_company_details


@click.group()
@click.option('--debug', default=False, is_flag=True, help='Enable debugging.')
def start(debug):
    pass


@click.command()
def companies(throttle=True, count=0, index="NYSE"):
    click.echo('companies')
    get_company_details(throttle, count, index)


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
