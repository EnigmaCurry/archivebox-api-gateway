from aiohttp import web

from mako.template import Template
import logging

log = logging.getLogger(__name__)


async def handle_404(request):
    template = Template(
        """
        Oh, too bad, that's a 404 :(
        """
    )
    log.debug(f"404: {request.path} {request.headers}")
    return web.Response(text=template.render(), content_type="text/html", status=404)


async def handle_500(request):
    template = Template(
        """
        Whoops, thats error 500.
        """
    )
    return web.Response(text=template.render(), content_type="text/html", status=500)


def create_error_middleware(overrides):
    @web.middleware
    async def error_middleware(request, handler):
        try:
            return await handler(request)
        except web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override:
                return await override(request)

            raise
        except Exception:
            request.protocol.logger.exception("Error handling request")
            return await overrides[500](request)

    return error_middleware


error_middleware = create_error_middleware({404: handle_404, 500: handle_500})
