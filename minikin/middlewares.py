# -*- coding: utf-8 -*-
"""
middlewares
"""
import logging

from aiohttp import web


logger = logging.getLogger('root')


def create_error_middleware(overrides):

    @web.middleware
    async def _error_middleware(request, handler):
        try:
            return await handler(request)
        except web.HTTPException as exc:
            try:
                return await overrides[exc.status](request)
            except KeyError:
                return web.json_response(
                    {'error': exc.text}, status=exc.status)
        except Exception:
            return await overrides[500](request)

    return _error_middleware


async def handle_404(request) -> web.Response:
    """json response for 404 Not Found"""
    return web.json_response(
        {'error': f'cannot find url {request.url}'}, status=404)


async def handle_500(request) -> web.Response:
    """json response for 500 Internal Error"""
    error = f'sorry, an unexpected error occurred. we are notified.'
    body = await request.text()
    logger.exception(
        'unepxected error for handling request=%s headers=%s body=%s',
        request, request.headers, body
    )
    return web.json_response({'error': error}, status=500)


error_middleware = create_error_middleware({
    404: handle_404,
    500: handle_500
})
