# -*- coding: utf-8 -*-
from aiohttp import web

from minikin.middlewares import error_middleware


async def test_404(aiohttp_client):
    app = web.Application()
    app.middlewares.append(error_middleware)
    client = await aiohttp_client(app)
    rsp = await client.get('/')
    assert rsp.status == 404
    data = await rsp.json()
    assert data == {'error': f'cannot find url {rsp.request_info.url}'}


async def test_500(aiohttp_client):

    async def _handler(request):
        raise

    app = web.Application()
    app.middlewares.append(error_middleware)
    app.router.add_get('/', _handler)
    client = await aiohttp_client(app)
    rsp = await client.get('/')
    assert rsp.status == 500
    data = await rsp.json()
    assert 'error' in data


async def test_other_error(aiohttp_client):

    async def _handler(request):
        return web.Response(status=200)

    app = web.Application()
    app.middlewares.append(error_middleware)
    app.router.add_get('/', _handler)
    client = await aiohttp_client(app)
    rsp = await client.post('/')  # this would raise 405 Method Not Allowed
    assert rsp.status == 405
    data = await rsp.json()
    assert 'error' in data
