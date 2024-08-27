from dependency_injector.wiring import Provide
from logging import getLogger, Logger
from pydantic_core import from_json
from asyncinit import asyncinit

from lslgwclient import API
from lslgwlib.enums import InvetoryType
from lslgwlib.models import Invetory, Avatar, Region

from lslframework.cache import Cache, Container
from lslframework.config import cfg, Runtime, SLShard
from lslframework.models.linksetdata import LinkSetData


@asyncinit
class LinkSet:
    """LSL linkset representation: read info about it and send commands"""

    # API from lsl-gatetway-client
    __clientAPI: API
    # Cache, by default redis
    __cache: Cache = Provide[Container.cache]
    # Pydantic model contains linkset information
    __linksetdata: LinkSetData
    __log: Logger

    # async def __init__(self, data: dict[str, Any]) -> None:
    async def __init__(self, *args, **kwargs) -> None:
        if (len(args) == 1 and isinstance(args[0], dict)) or (
            "headers" in kwargs and isinstance(kwargs["headers"], dict)
        ):
            if "headers" in kwargs:
                headers = kwargs["headers"]
            else:
                headers = args[0]
            headers = {k.lower(): v for k, v in headers.items()}
            oid = headers["x-secondlife-object-key"]
            name = headers["x-secondlife-object-name"]
            owner = Avatar(
                headers["x-secondlife-owner-key"], headers["x-secondlife-owner-name"]
            )
            region = Region(headers["x-secondlife-region"])
            if headers["x-secondlife-shard"] == "Production":
                shard = SLShard.production
            else:
                shard = SLShard.testing
        elif (
            "id" in kwargs
            and "name" in kwargs
            and "owner" in kwargs
            and "region" in kwargs
            and "production" in kwargs
        ):
            oid = kwargs["id"]
            name = kwargs["name"]
            owner = kwargs["owner"]
            region = kwargs["region"]
            if kwargs["production"]:
                shard = SLShard.production
            else:
                shard = SLShard.testing
        else:
            raise ValueError()

        # setup logger
        self.__log = getLogger(str(oid))
        # setup API
        self.__clientAPI = API()

        # use fake HTTP provider in testing environment
        if cfg.app.runtime == Runtime.testing:
            from tests.fakes.http import HTTP

            self.__clientAPI.container.http.override(HTTP)

        # load LSL linkset data from cache if exist
        # or load directly by lsl-gatetway-client
        lsJson = await self.__cache.getLinkSet(oid, shard)
        lsAuthToken = await self.__cache.readAuthToken(oid, shard)
        if not lsAuthToken:
            raise RuntimeError("Auth token is not exist")
        if not lsJson:
            self.__linksetdata = LinkSetData(
                id=oid,
                name=name,
                owner=owner,
                region=region,
                shard=shard,
            )
        else:
            self.__linksetdata = LinkSetData.model_validate(from_json(lsJson))
            self.__linksetdata.name = name
            self.__linksetdata.owner = owner
            self.__linksetdata.region = region
            self.__linksetdata.shard = shard

        await self.save()

    async def inventoryGet(self, bytype: InvetoryType = InvetoryType.ANY) -> Invetory:
        """Load linkset inventory

        Arguments:
        bytype - filter, enum from lsl-gateway-lib
        """

        # cache already contains actual data
        if (
            await self.load()
            and self.__linksetdata.inventory
            and self.__linksetdata.inventory.filtered == bytype
        ):
            return self.__linksetdata.inventory
        else:
            # load from linkset
            ls = await self.linkset()
            # save to self.__linksetdata
            resp = await ls.inventoryRead(bytype)
            if isinstance(resp.data, Invetory):
                self.__linksetdata.inventory = resp.data
            else:
                self.__linksetdata.inventory = None
            # save to cache
            await self.save()
        if not self.__linksetdata.inventory:
            raise ValueError()
        return self.__linksetdata.inventory

    async def inventorySet(self, inventory: Invetory | None = None):
        """Set inventory data and save to cache

        Arguments:
        inventory - Inventory pydantic model from lsl-gateway-lib
        """
        self.__linksetdata.inventory = inventory
        await self.save()

    async def load(self) -> bool:
        """load from cache"""
        json = await self.__cache.getLinkSet(
            self.__linksetdata.id, self.__linksetdata.shard
        )
        if json:
            self.__log.debug(json)
            self.__linksetdata = LinkSetData.model_validate(from_json(json))
            return True
        return False

    async def save(self) -> None:
        """Update cache"""
        await self.__cache.setLinkSet(self.__linksetdata, self.__linksetdata.shard)

    async def authToken(self) -> str:
        lsAuthToken = await self.__cache.readAuthToken(
            self.__linksetdata.id, self.__linksetdata.shard
        )
        if not lsAuthToken:
            raise RuntimeError("Auth token is not exist")
        return lsAuthToken

    async def linkset(self):
        return self.__clientAPI.linkset(
            "https://simhost-0123456789abcdef0.agni.secondlife.io:12043"
            + "/cap/00000000-0000-0000-0000-000000000000",
            headers={"X-Auth-Token": await self.authToken()},
        )
