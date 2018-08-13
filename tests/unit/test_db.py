# -*- coding: utf-8 -*-
from unittest.mock import Mock, patch

from aioredis.commands import Redis
import pytest

from minikin.db import (
    URLNotFound, write_to_redis_if_exists, shorten_url, get_url)
from .helpers import FakeConnection, make_future


async def test_write_to_redis_when_redis_is_none():
    result = await write_to_redis_if_exists('key', 'value', None)
    assert result is None


async def test_write_to_redis_succeed():
    redis = Mock(spec=Redis)
    redis.set.return_value = make_future(True)
    result = await write_to_redis_if_exists('key', 'value', redis)
    assert result is None


async def test_write_to_redis_throw_exception():
    redis = Mock(spec=Redis)
    redis.set.return_value = make_future(exception=RuntimeError)
    with patch('minikin.db.logger') as logger:
        await write_to_redis_if_exists('key', 'value', redis)
    logger.warning.assert_called()


async def test_shorten_url():
    pool = Mock(**{'acquire.return_value': FakeConnection()})
    result = await shorten_url(
        pool, 'https://minik.in/long-url', size=7, redis=None)
    assert result == 'PTFeSGv'


async def test_get_url_without_redis():
    url = 'https://minik.in/long-url'
    pool = Mock(**{
        'acquire.return_value': FakeConnection({'fetchrow': {'url': url}})
    })
    result = await get_url(pool, 'PTFeSGv', None)
    assert result == url


async def test_get_url_found_in_redis():
    url = 'https://minik.in/long-url'
    pool = Mock()
    redis = Mock(spec=Redis)
    redis.get.return_value = make_future(url)
    result = await get_url(pool, 'PTFeSGv', redis)
    assert result == url
    pool.acquire.assert_not_called()


async def test_get_url_not_found_in_redis_but_found_in_db():
    url = 'https://minik.in/long-url'
    pool = Mock(**{
        'acquire.return_value': FakeConnection({'fetchrow': {'url': url}})
    })
    redis = Mock(spec=Redis)
    redis.get.return_value = make_future()
    with patch('minikin.db.write_to_redis_if_exists',
               return_value=make_future()) as patched:
        result = await get_url(pool, 'PTFeSGv', redis)
    assert result == url
    patched.assert_called_once()


async def test_get_url_not_found_in_redis_nor_db():
    slug = 'PTFeSGv'
    pool = Mock(**{'acquire.return_value': FakeConnection()})
    redis = Mock(spec=Redis)
    redis.get.return_value = make_future()
    with pytest.raises(URLNotFound) as exc:
        await get_url(pool, slug, redis)
    assert exc.value.slug == slug
