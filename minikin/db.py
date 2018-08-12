# -*- coding: utf-8 -*-
"""
database operations
"""
import logging

from asyncpg.pool import Pool
from aioredis.commands import Redis
from .utils import generate_slug

logger = logging.getLogger('root')


class URLNotFound(Exception):
    """
    url doesn't exist for slug
    """
    def __init__(self, slug):
        self.slug = slug
        super().__init__(slug)


async def write_to_redis_if_exists(key, value, redis: Redis=None):
    if redis:
        try:
            await redis.set(key, value)
        except Exception:
            logger.warning('error set cache key=%s value=%s', key, value)


async def shorten_url(
        pool: Pool, url: str, size: int, redis: Redis=None) -> str:
    """
    shorten url
    """
    slug = generate_slug(url, size)
    async with pool.acquire() as connection:
        async with connection.transaction():
            # do an upsert and ignore hash collision as the probability
            # is extremely low, however, if collision is to be eliminated
            # completely, it can be done in sacrifice of efficiency.
            await connection.execute(
                '''
                INSERT INTO short_url(slug, url)
                VALUES($1, $2)
                ON CONFLICT (slug) DO NOTHING;
                ''', slug, url
            )
    await write_to_redis_if_exists(slug, url, redis)
    return slug


async def get_url(pool: Pool, slug: str, redis: Redis=None) -> str:
    """
    get url for slug
    """
    if redis:
        url = await redis.get(slug)
        if url:
            logger.debug('found from cache %s -> %s', slug, url)
            return url

    async with pool.acquire() as connection:
        record = await connection.fetchrow(
            'SELECT * FROM short_url WHERE slug = $1', slug)
        if not record:
            raise URLNotFound(slug)
        url = record['url']
        await write_to_redis_if_exists(slug, url, redis)
        return url
