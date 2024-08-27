from dependency_injector.wiring import Provide, inject
from logging import getLogger
from fastapi import Request
from uuid import UUID

from lslframework.cache.cache import Cache
from lslframework.cache.container import Container
from lslframework.config import cfg, SLShard

log = getLogger(__name__)


# verify request
@inject
async def allowed(req: Request, cache: Cache = Provide[Container.cache]) -> bool:
    # SL shard
    if "x-secondLife-shard" not in req.headers:
        log.error("Not shard selected in request")
        log.debug(req.headers)
        return False
    if req.headers["x-secondLife-shard"].lower() not in [
        x.name for x in cfg.app.shards
    ]:
        log.error(f"Not allowed shard in request '{req.headers['x-secondLife-shard']}'")
        log.debug(req.headers)
        return False

    # LSL linkset id
    if "x-secondlife-object-key" not in req.headers:
        log.error("Not exist LSL object id in request")
        log.debug(req.headers)
        return False
    # Auth token
    if "x-auth-token" not in req.headers:
        log.error("Not exist auth token in request")
        log.debug(req.headers)
        return False
    # compare token given by request and token in cache
    if req.headers["x-secondLife-shard"] == "Production":
        shard = SLShard.production
    else:
        shard = SLShard.testing
    if (
        await cache.readAuthToken(UUID(req.headers["x-secondlife-object-key"]), shard)
        != req.headers["x-auth-token"].lower()
    ):
        log.error("Invalid auth token in request")
        log.debug(req.headers)
        return False

    return True
