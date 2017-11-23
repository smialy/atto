import aioredis

from atto_api.cdi import activator
from atto_api.services import ICache, ISessionStore


class RedisCache:
    def __init__(self, host, port):
        self._host = host
        self._port = port

    async def connect(self):
        self.redis = await aioredis.create_pool((
            self._host, self._port
        ))

    async def close(self):
        self.redis.close()
        await self.redis.wait_closed()

    async def set(self, name, value):
        await self.redis.set(name, value)

    async def get(self, name):
        return await self.redis.get(name)

    async def load(self, key):
        return await self.get(key)

    async def save(self, key, value):
        await self.set(key, value)


@activator
class CacheActivator:
    async def start(self, ctx):
        props = ctx.get_property('REDIS')
        self.service = RedisCache(props['host'], props['port'])
        await self.service.connect()
        classes = (ICache, ISessionStore)
        self.reg = ctx.register_service(classes, self.service, {
            'name': 'redis'
        })

    async def stop(self, ctx):
        self.reg.unregister()
        await self.service.close()
