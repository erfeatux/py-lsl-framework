import abc
from uuid import UUID

from lslframework.models.linksetdata import LinkSetData
from lslframework.config import SLShard


class Cache(abc.ABC):
    """Cache provides caching functions
    by default it is replaced by redis cache from rediscache.py using dependency-injector
    """

    @abc.abstractmethod
    async def getLinkSet(self, id: UUID, shard: SLShard) -> str | None:
        """GetLinkSet returns json representationof LSL object

        Arguments:
        id -    UUID, LSL object key
        shard - SLShard enum, SL shard production = Agni or testing = Aditi
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def setLinkSet(self, data: LinkSetData, shard: SLShard) -> None:
        """setLinkSet stores the LSL object in cache as json

        Arguments:
        data -  LinkSetData pydantic model
        shard - SLShard enum, SL shard production = Agni or testing = Aditi
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def writeAuthToken(self, id: UUID, token: str, shard: SLShard) -> None:
        """writeAuthToken - stores auth token in cache as string

        Arguments:
        id -    UUID, LSL object key
        token - token string
        shard - SLShard enum, SL shard production = Agni or testing = Aditi
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def readAuthToken(self, id: UUID, shard: SLShard) -> str | None:
        """readAuthToken - returns auth token string

        Arguments:
        id -    UUID, LSL object key
        shard - SLShard enum, SL shard production = Agni or testing = Aditi
        """
        raise NotImplementedError()
