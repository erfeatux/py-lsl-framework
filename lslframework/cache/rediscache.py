from logging import getLogger, Logger
from pydantic import TypeAdapter
from uuid import UUID
import redis

from .cache import Cache as BaseCache
from lslframework.models.linksetdata import LinkSetData
from lslframework.config import cfg, SLShard


# connection fabric
class RedisConnection:
    __shard: SLShard
    __rds: redis.asyncio.Redis

    def __init__(self, shard: SLShard):
        self.__shard = shard

    async def __aenter__(self) -> redis.asyncio.Redis:
        addr = (  # different db per SL shard
            str(cfg.redis.connectionProdShard)
            if self.__shard == SLShard.production
            else str(cfg.redis.connectionTestShard)
        )
        self.__rds = redis.asyncio.Redis.from_url(addr)
        if not await self.__rds.ping():
            raise redis.ConnectionError()
        return self.__rds

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.__rds.aclose()


class Cache(BaseCache):
    __log: Logger

    def __init__(self) -> None:
        self.__log = getLogger(self.__class__.__name__)

    async def getLinkSet(self, id: UUID, shard: SLShard) -> str | None:
        self.__log.debug(f"{id=}, {shard=}")
        async with RedisConnection(shard) as rds:
            ret = await rds.get(f"lslobject.{id}")
            if ret:
                return ret.decode("UTF-8")
        return None

    async def setLinkSet(self, data: LinkSetData, shard: SLShard) -> None:
        self.__log.debug(f"{data=}, {shard=}")
        async with RedisConnection(shard) as rds:
            ta = TypeAdapter(LinkSetData)
            await rds.set(f"lslobject.{data.id}", ta.dump_json(data).decode("UTF-8"))

    async def writeAuthToken(self, id: UUID, token: str, shard: SLShard) -> None:
        self.__log.debug(f"{id=}, {token=}, {shard=}")
        async with RedisConnection(shard) as rds:
            await rds.set(f"lslobject.token.{id}", token.encode("UTF-8"))

    async def readAuthToken(self, id: UUID, shard: SLShard) -> str | None:
        self.__log.debug(f"{id=}, {shard=}")
        async with RedisConnection(shard) as rds:
            ret = await rds.get(f"lslobject.token.{id}")
            if ret:
                return ret.decode("UTF-8")
        return None
