
from aiohttp import web

from atto_api.cdi import activator
from atto_api.web import IWebApplication


class Sources:
    def get(self, request):
        pass

    def post(self, request):
        pass

    def match(self, request):
        pass


def aiohttp_middleware(cdi):
    async def atto_middleware(app, handler):
        async def middleware(request):
            result = await handler(cdi, request)
            if result:
                return result
            return web.Response(text=result or '')
        return middleware
    return atto_middleware


@activator
class WebHandlers:
    def start(self, ctx):
        app = web.Application(middlewares=[])
        ctx.register_service(IWebApplication, app)

    def stop(self, ctx):
        pass
