from fastapi import APIRouter, Request, Header, Depends
from dependency_injector.wiring import Provide, inject
from fastapi.responses import PlainTextResponse
from logging import getLogger
from typing import Annotated
from secrets import randbits
from hashlib import sha512
from pydantic import Field
from uuid import UUID
import re

from lslframework.config import cfg, SLShard
from lslframework.cache import Cache, Container


log = getLogger(__name__)
router = APIRouter(prefix="/lsl", tags=["lsl"])


# auth LSL object, returns auth token
@router.post("/auth", response_class=PlainTextResponse)
@inject
async def auth(
    req: Request,
    # sign, body contains random string signed by application token
    sign: Annotated[str, Field(pattern=re.compile(r"[0-9a-f]{128}"))],
    # LSL linkset id
    x_secondlife_object_key: Annotated[UUID | None, Header()] = None,
    x_secondlife_shard: Annotated[SLShard | None, Header()] = None,
    cache: Cache = Depends(Provide[Container.cache]),
) -> PlainTextResponse:
    # not LSL linkset
    if not x_secondlife_object_key:
        return PlainTextResponse(status_code=403)
    if not x_secondlife_shard:
        return PlainTextResponse(status_code=403)

    # calc sign from body string
    calc = sha512(await req.body())
    calc.update(cfg.app.token.encode("UTF-8"))
    verify = calc.hexdigest()

    # compare sign given by request and calculated sign
    if sign.lower() == verify.lower():
        # generate random token
        token = sha512(randbits(512).to_bytes(64, "big"))
        # save it to cache
        await cache.writeAuthToken(
            x_secondlife_object_key, token.hexdigest(), x_secondlife_shard
        )
        # return it
        return PlainTextResponse(token.hexdigest())

    # default response
    return PlainTextResponse(status_code=403)
