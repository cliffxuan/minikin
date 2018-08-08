# -*- coding: utf-8 -*-
"""
http handlers
"""
import logging
import json

from aiohttp import web

from .utils import validate_url
from . import db


logger = logging.getLogger('root')


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
        raise web.HTTPNotFound


async def shorten_url(request) -> web.Response:
    """convert a long url from json body into a short url"""
    body = await request.text()
    try:
        url = json.loads(body)['url']
    except (json.decoder.JSONDecodeError, KeyError):
        example = '{"url": "www.helloworld.com"}'
        error = f'invalid request body {body}, expected format {example}'
        return web.json_response({'error': error}, status=400)
    try:
        url = validate_url(url)
    except ValueError:
        return web.json_response(
            {'error': f'cannot shorten an invalid url {url}'}, status=400)
    settings = request.app['settings']
    shortened = await db.shorten_url(
        request.app['pool'], url, settings['length'], settings['base_url'])
    return web.json_response({'shortened_url': shortened}, status=201)
