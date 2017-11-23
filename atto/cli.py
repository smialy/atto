import asyncio
import os
from functools import wraps

import aiohttp

import click

from .main import create_app
from .models import Users
from .settings import Settings
from .utils.migration import yoyo_new, yoyo_prepare
from .utils.user import check_password, encrypt_password
from .version import VERSION


def async_helper_app(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        loop = asyncio.get_event_loop()
        app = loop.run_until_complete(create_app(loop))
        loop.run_until_complete(app.startup())
        if asyncio.iscoroutinefunction(fn):
            loop.run_until_complete(fn(app, *args, **kwargs))
        else:
            fn(app, *args, **kwargs)
        loop.run_until_complete(app.cleanup())
    return decorator


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('--env-file', '-e', type=click.File())
@click.pass_context
def cli(ctx, debug, env_file):
    if env_file:
        for line in env_file:
            if line.strip():
                key, value = line.split('=')
                os.environ[key.strip()] = value.strip()
    ctx.obj = dict(DEBUG=debug)


@cli.command()
@click.argument('login', type=str, required=True)
@click.option('--username', prompt=True,
              default=lambda: os.environ.get('USER', ''))
@click.password_option()
@click.pass_context
@async_helper_app
async def adduser(app, ctx, login, username, password):
    password_hash = encrypt_password(password)
    users = Users(app['db'])
    user = await users.find_by_login(login)
    if user:
        print('User: "{}" already exists.'.format(login))
    else:
        id = await users.add(login, password_hash, username)
        print('User "{}[{}]" added.'.format(login, id))


@cli.command()
@click.argument('login', type=str, required=True)
@click.password_option()
@click.pass_context
@async_helper_app
async def passwd(app, ctx, login, password):
    password_hash = encrypt_password(password)
    users = Users(app['db'])
    user = await users.find_by_login(login)
    if user:
        await users.passwd(user['id'], password_hash)
        print('User: "{}" password changed.'.format(login))
    else:
        print('Not found user: "{}".'.format(login))


@cli.command()
@click.argument('login', type=str, required=True)
@async_helper_app
async def deluser(app, login):
    users = Users(app['db'])
    user = await users.find_by_login(login)
    if user:
        await users.remove(user['id'])
        print('User: "{}" removed.'.format(login))
    else:
        print('Not found user: "{}".'.format(login))


@cli.command()
@click.argument('login', type=str, required=True)
@async_helper_app
async def lockuser(app, login):
    users = Users(app['db'])
    user = await users.find_by_login(login)
    if user:
        await users.lock(user['id'])
        print('User: "{}" locked.'.format(login))
    else:
        print('Not found user: "{}".'.format(login))


@cli.command()
@click.argument('login', type=str, required=True)
@async_helper_app
async def unlockuser(app, login):
    users = Users(app['db'])
    user = await users.find_by_login(login)
    if user:
        await users.unlock(user['id'])
        print('User: "{}" unlocked.'.format(login))
    else:
        print('Not found user: "{}".'.format(login))


@cli.command()
@async_helper_app
async def test(app):
    users = Users(app['db'])
    id = await users.add_user('a', 'a', 'a')


@cli.group()
def yoyo():
    pass


@yoyo.command()
def apply():
    backend, migrations = yoyo_prepare(Settings())
    backend.apply_migrations(backend.to_apply(migrations))


@yoyo.command()
def rollback():
    backend, migrations = yoyo_prepare(Settings())
    backend.rollback_migrations(backend.to_rollback(migrations))


@yoyo.command()
@click.argument('message', type=str, required=True)
def new(message):
    yoyo_new(message)


@cli.command()
def runserver():
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(create_app(loop))
    aiohttp.web.run_app(app)
