#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import logging.config

import asyncio
import asyncpg
from aiohttp import web

import handlers


def get_logger() -> logging.Logger:
    """
    a simple logger that logs to both console and file
    """
    LOGGING = {
        'version': 1,
        'formatters': {
            'simple': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': 'output.log',
                'formatter': 'simple'
            },
        },
        'loggers': {
            'root': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG'
            }
        }
    }
    logging.config.dictConfig(LOGGING)
    return logging.getLogger('root')


logger = get_logger()


def create_error_middleware(overrides):

    @web.middleware
    async def error_middleware(request, handler):
        try:
            return await handler(request)
        except web.HTTPException as exc:
            try:
                return await overrides[exc.status](request)
            except KeyError:
                raise
        except Exception:
            try:
                return await overrides[500](request)
            except KeyError:
                raise

    return error_middleware


async def init_app(database, user, length, base_url):
    app = web.Application()
    app['settings'] = {'length': length, 'base_url': base_url}
    app['pool'] = await asyncpg.create_pool(
        database=database, user=user)
    app.router.add_get(r'/{slug:[0-9a-zA-z]{%d}}' % length, handlers.get_url)
    app.router.add_post('/shorten_url', handlers.shorten_url)
    error_middleware = create_error_middleware({
        404: handlers.handle_404,
        500: handlers.handle_500
    })
    app.middlewares.append(error_middleware)
    return app


def argument_parser():
    parser = argparse.ArgumentParser(
        description='minikin the minimal url shortner with super power')
    parser.add_argument(
        'database', nargs='?', help='database name', default='minikin')
    parser.add_argument(
        '--user', '-u', help='database user', default='postgres')
    parser.add_argument(
        '--length', help='length of the short url path', type=int, default=7)
    parser.add_argument(
        '--base-url', help='base url', default='http://localhost:8080')
    return parser


def main(argv=None):
    args = argument_parser().parse_args(argv)
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(
        init_app(args.database, args.user, args.length, args.base_url)
    )
    web.run_app(app)


if __name__ == '__main__':
    main()
