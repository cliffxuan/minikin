#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
entry point of the application
"""
import argparse
import logging
import logging.config

import asyncio
import asyncpg
import uvloop
from aiohttp import web

from minikin import handlers, middlewares


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


async def init_app(database, user, length, base_url):
    app = web.Application()
    app['settings'] = {'length': length, 'base_url': base_url}
    app['pool'] = await asyncpg.create_pool(database=database, user=user)
    app.router.add_get('/', handlers.index)
    app.router.add_static('/static', 'static')
    app.router.add_get(r'/{slug:[0-9a-zA-z]{%d}}' % length, handlers.get_url)
    app.router.add_post('/shorten_url', handlers.shorten_url)
    app.middlewares.append(middlewares.error_middleware)
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
    parser.add_argument('--path', help='path', default=None)
    parser.add_argument('--port', help='port', default=None)
    return parser


def main(argv=None):
    args = argument_parser().parse_args(argv)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(
        init_app(args.database, args.user, args.length, args.base_url)
    )
    web.run_app(app, path=args.path, port=args.port)


if __name__ == '__main__':
    main()
