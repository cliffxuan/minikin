# -*- coding: utf-8 -*-
import asyncio
import json
from unittest.mock import Mock, patch

from aiohttp import web

from minikin.handlers import get_url, shorten_url, index
from minikin.db import URLNotFound


async def test_get_url_with_url_exists(aiohttp_client):
    app = web.Application()
    app.router.add_get('/{slug:[0-9a-zA-z]{3}}', get_url)
    app['pool'] = Mock()
    client = await aiohttp_client(app)
    future = asyncio.Future()
    dest = 'https://minik.in'
    with patch('minikin.handlers.db.get_url', return_value=future):
        future.set_result(dest)
        rsp = await client.get('/abc', allow_redirects=False)
    assert rsp.status == 302
    assert rsp.headers['location'] == dest


async def test_get_url_with_url_not_exists(aiohttp_client):
    app = web.Application()
    app.router.add_get('/{slug:[0-9a-zA-z]{3}}', get_url)
    app['pool'] = Mock()
    client = await aiohttp_client(app)
    future = asyncio.Future()
    with patch('minikin.handlers.db.get_url', return_value=future):
        future.set_exception(URLNotFound())
        rsp = await client.get('/abc', allow_redirects=False)
    assert rsp.status == 404


async def test_shorten_url_body_correct_json_invalid_url(aiohttp_client):
    app = web.Application()
    app['pool'] = Mock()
    app['settings'] = {'length': 3, 'base_url': 'https://minik.in'}
    app.router.add_post('/', shorten_url)
    client = await aiohttp_client(app)
    future = asyncio.Future()
    shortened = 'https://minik.in/abc'
    with patch('minikin.handlers.db.shorten_url', return_value=future):
        future.set_result(shortened)
        rsp = await client.post('/', data=json.dumps(
            {'url': 'hello world'}))
    assert rsp.status == 400


async def test_shorten_url_body_not_json(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', shorten_url)
    client = await aiohttp_client(app)
    rsp = await client.post('/', data='abc')
    assert rsp.status == 400


async def test_shorten_url_body_wrong_format_json(aiohttp_client):
    app = web.Application()
    app.router.add_post('/', shorten_url)
    client = await aiohttp_client(app)
    rsp = await client.post('/', data=json.dumps(
        {'wrong_key': 'https://minik.in'}))
    assert rsp.status == 400


async def test_shorten_url_body_correct_json_valid_url(aiohttp_client):
    app = web.Application()
    app['pool'] = Mock()
    app['settings'] = {'length': 3, 'base_url': 'https://minik.in'}
    app.router.add_post('/', shorten_url)
    client = await aiohttp_client(app)
    future = asyncio.Future()
    shortened = 'https://minik.in/abc'
    with patch('minikin.handlers.db.shorten_url', return_value=future):
        future.set_result(shortened)
        rsp = await client.post('/', data=json.dumps(
            {'url': 'https://helloworld.com'}))
    assert rsp.status == 201
    data = await rsp.json()
    assert data['shortened_url'] == shortened


async def test_index(aiohttp_client):
    app = web.Application()
    app.router.add_get('/', index)
    client = await aiohttp_client(app)
    rsp = await client.get('/')
    assert rsp.status == 200
    assert rsp.content_type == 'text/html'
    assert rsp.charset == 'utf8'
