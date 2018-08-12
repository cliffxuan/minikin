# -*- coding: utf-8 -*-
"""
http handlers
"""
import logging
import json
import os

from aiohttp import web

from .utils import validate_url
from . import db


logger = logging.getLogger('root')


async def get_url(request) -> web.Response:
    """redirect to the destination url from the short url"""
    slug = request.match_info['slug']
    try:
        url = await db.get_url(request.app['pool'], slug, request.app['redis'])
    except db.URLNotFound:
        raise web.HTTPNotFound
    return web.HTTPFound(
        location=url,
        content_type='application/json',
        body=json.dumps({'location': url})
    )


async def shorten_url(request) -> web.Response:
    """convert a long url from json body into a short url"""
    body = await request.text()
    logger.info(body)
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
    slug = await db.shorten_url(
        request.app['pool'], url, settings['length'], request.app['redis'])
    shortened_url = f'{settings["base_url"]}/{slug}'
    return web.json_response({'shortened_url': shortened_url}, status=201)


async def index(request) -> web.Response:
    with open(os.path.join(os.path.dirname(__file__), '../index.html')) as fo:
        return web.Response(
            status=200,
            body=fo.read(),
            content_type='text/html',
            charset='utf8'
        )
