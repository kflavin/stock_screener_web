import click
from populators.companies import get_company_details
from populators.external.sectors import get_sector_and_industry
from populators.sectors import get_sectors_and_industries
from populators.indicators import get_ratio_data


@click.group()
@click.option('--debug', default=False, is_flag=True, help='Enable debugging.')
@click.option('--host', default="http://127.0.0.1:5000", help='Web API', envvar='CLI_HOST')
@click.option('--user', help='API user', envvar='CLI_USER')
@click.option('--password', help='API password', envvar='CLI_PASSWORD')
@click.pass_context
def cli(ctx, debug, host, user, password):
    ctx.obj['DEBUG'] = debug
    ctx.obj['HOST'] = host
    ctx.obj['USER'] = user
    ctx.obj['PASSWORD'] = password


@cli.command()
@click.option('--no-throttle', default=True, is_flag=True, help='Throttle connection')
@click.option('--count', default=0, help='Number of companies to retrieve')
@click.option('--exchange', default="NYSE", help='Exchange NYSE|NASDAQ')
@click.pass_context
def companies(ctx, no_throttle, count, exchange):
    click.echo('Retrieving Companies, settings: {} {} {}'.format(no_throttle, count, exchange))
    get_company_details(no_throttle, count, exchange, ctx.obj['HOST'], ctx.obj['USER'], ctx.obj['PASSWORD'])


@cli.command()
@click.option('--count', default=None, help='Per page number to retrieve')
@click.pass_context
def indicators(ctx, count):
    click.echo('Retrieving {}'.format(ctx.obj))
    get_ratio_data(count, ctx.obj['HOST'], ctx.obj['USER'], ctx.obj['PASSWORD'])


@cli.command()
@click.option('--symbol', default=None, help='Symbol for single company')
@click.option('--count', default=None, help='Per page number to retrieve')
@click.pass_context
def sectors(ctx, symbol, count):
    click.echo('sectors')
    if symbol:
        click.echo("get company {}".format(symbol))
        # If we have a single symbol, just make the external call directly, rather than through our populator
        print get_sector_and_industry(symbol, ctx.obj['HOST'], ctx.obj['USER'], ctx.obj['PASSWORD'])
    else:
        get_sectors_and_industries(count, ctx.obj['HOST'], ctx.obj['USER'], ctx.obj['PASSWORD'])


cli.add_command(companies)
cli.add_command(indicators)
cli.add_command(sectors)

if __name__ == '__main__':
    cli(obj={})
