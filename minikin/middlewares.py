# -*- coding: utf-8 -*-
"""
middle wares
"""
import logging
import json

from aiohttp import web


logger = logging.getLogger('root')


def create_error_middleware(overrides):

    @web.middleware
    async def error_middleware(request, handler):
        try:
            return await handler(request)
        except web.HTTPException as exc:
            try:
                return await overrides[exc.status](request)
            except KeyError:
                raise
        except Exception:
            try:
                return await overrides[500](request)
            except KeyError:
                raise

    return error_middleware


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


error_middleware = create_error_middleware({
    404: handle_404,
    500: handle_500
})
