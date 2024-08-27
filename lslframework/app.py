from fastapi import FastAPI
import logging

from lslgwserver.routers import onChangedRouter
from lslgwserver.models import LSLRequest
from lslgwlib.enums import Change

from .models import LinkSet
from .cache.container import Container
from lslframework.routers import authRouter
from lslframework.config import cfg, LogLevel
import lslframework.models.linkset
import lslframework.routers.auth
import lslframework.auth.auth


# wiring dependency-injector
container = None
if not container:
    container = Container()
    container.wire(
        packages=[
            lslframework.models.linkset,
            lslframework.routers.auth,
            lslframework.auth.auth,
        ]
    )

match cfg.app.logLevel:
    case LogLevel.debug:
        level = logging.DEBUG
    case LogLevel.warning:
        level = logging.WARNING
    case LogLevel.error:
        level = logging.ERROR
    case LogLevel.critical:
        level = logging.CRITICAL
    case _:
        level = logging.INFO
logging.basicConfig(
    format="%(asctime)-15s %(levelname)-8s| %(name)s.%(funcName)s: %(message)s",
    level=level,
)

log = logging.getLogger(__name__)


class App:
    """LSL framework application"""

    __fastapi: FastAPI

    def __init__(self, fastapi: FastAPI) -> None:
        self.__fastapi = fastapi
        # routers
        self.__fastapi.include_router(onChangedRouter)
        self.__fastapi.include_router(authRouter)
        # setup auth dependency
        onChangedRouter.container.allow.override(lslframework.auth.auth)
        # register callbacks
        onChangedRouter.addCallback(self.__onChange)

    # https://wiki.secondlife.com/wiki/Changed
    async def __onChange(self, req: LSLRequest) -> bool:
        log.info(req)
        ls = await LinkSet(
            id=req.objectKey,
            name=req.objectName,
            owner=req.owner,
            region=req.region,
            production=req.production,
        )
        match req.data:
            case Change.INVENTORY:
                # drop inventory from cache
                await ls.inventorySet()
        return True
