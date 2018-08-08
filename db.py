# -*- coding: utf-8 -*-
"""
database operations
"""
from asyncpg.pool import Pool

from utils import generate_slug


class URLNotFound(Exception):
    """
    url doesn't exist for slug
    """


async def shorten_url(pool: Pool, url: str, size: int, base: str):
    """
    shorten url
    """
    slug = generate_slug(url, size)
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                '''
                INSERT INTO short_url(slug, url)
                VALUES($1, $2)
                ON CONFLICT (slug) DO NOTHING;
                ''', slug, url
            )
    return f'{base}/{slug}'


async def get_url(pool: Pool, slug: str) -> str:
    """
    get url for slug
    """
    async with pool.acquire() as connection:
        record = await connection.fetchrow(
            'SELECT * FROM short_url WHERE slug = $1', slug)
        if not record:
            raise URLNotFound(slug)
        return record['url']
