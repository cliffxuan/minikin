#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
script for generating cache
"""
import argparse
import sys

import aioredis
import asyncio
import asyncpg


def argument_parser():
    parser = argparse.ArgumentParser(description='generate cache')
    parser.add_argument(
        'database', nargs='?', help='database name', default='minikin')
    parser.add_argument(
        '--user', '-u', help='database user', default='postgres')
    parser.add_argument(
        '--redis', '-r', help='redis uri', dest='redis_uri',
        default='redis://localhost')
    return parser


async def load_cache(database, user, redis_uri):
    pool = await asyncpg.create_pool(database=database, user=user)
    redis = await aioredis.create_redis_pool(
        redis_uri, encoding='utf-8', minsize=5, maxsize=10)

    async with pool.acquire() as connection:
        record = await connection.fetchrow('SELECT COUNT(slug) from short_url')
        count = record['count']
        print(f'start loading.\ntotal record {count}.')
        i = 0
        async with connection.transaction():
            async for record in connection.cursor('SELECT * FROM short_url'):
                await redis.set(record['slug'].strip(), record['url'])
                i += 1
                if i % 100 == 0:
                    sys.stdout.write(f'\r{i / count * 100:.2f}%')
                    sys.stdout.flush()
            else:
                sys.stdout.write('\r100.00%\n')
        print('done!')


def main(argv=None):
    args = argument_parser().parse_args(argv)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        load_cache(args.database, args.user, args.redis_uri))


if __name__ == '__main__':
    main()
