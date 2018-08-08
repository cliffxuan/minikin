# -*- coding: utf-8 -*-
"""
http handlers
"""
import logging
import json

from aiohttp import web

from utils import validate_url
import db


logger = logging.getLogger('root')


async def handle_404(request) -> web.Response:
    """json response for 404 Not Found"""
    return web.Response(
        status=404,
        content_type='application/json',
        charset='utf8',
        body=json.dumps({'error': f'cannot find url for {request.url}'})
    )


async def handle_500(request) -> web.Response:
    """json response for 500 Internal Error"""
    error = f'sorry, an unexpected error occurred. we are notified.'
    body = await request.text()
    logger.exception(
        'unepxected error for handling request=%s headers=%s body=%s',
        request, request.headers, body
    )
    return web.Response(
        status=500,
        content_type='application/json',
        charset='utf8',
        body=json.dumps({'error': error})
    )


async def get_url(request) -> web.Response:
    """redirect to the destination url from the short url"""
    try:
        url = await db.get_url(request.app['pool'], request.match_info['slug'])
        return web.HTTPFound(
            location=url,
            content_type='application/json',
            body=json.dumps({'location': url})
        )
    except db.URLNotFound:
        raise web.HTTPNotFound()


async def shorten_url(request) -> web.Response:
    """convert a long url from json body into a short url"""
    body = await request.text()
    try:
        url = json.loads(body)['url']
    except (json.decoder.JSONDecodeError, KeyError):
        example = '{"url": "www.helloworld.com"}'
        error = f'invalid request body {body}, expected format {example}'
        return web.Response(
            status=400,
            content_type='application/json',
            charset='utf8',
            body=json.dumps({'error': error})
        )
    if not validate_url(url):
        return web.Response(
            status=400,
            content_type='application/json',
            charset='utf8',
            body=json.dumps({
                'error': f'cannot shorten an invalid url {url}'
            })
        )
    settings = request.app['settings']
    shortened = await db.shorten_url(
        request.app['pool'], url, settings['length'], settings['base_url'])
    return web.Response(
        status=201,
        content_type='application/json',
        charset='utf8',
        body=json.dumps({'shortened_url': shortened})
    )
