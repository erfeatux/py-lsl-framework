from secrets import randbits
from hashlib import sha512
from uuid import uuid4
import asyncio
import pytest
import httpx

from aiohttp.web_exceptions import HTTPForbidden

from lslframework.models import LinkSet
from lslgwlib.enums import InvetoryType, Change

from tests.fakes.http import addInvData, inventoryData, setAuthToken


def test_test(auth_token, http_service, headers):
    ls: LinkSet = asyncio.run(LinkSet(headers))

    inventory = asyncio.run(ls.inventoryGet())
    assert len(inventory.items) == 4
    assert inventory.filtered == InvetoryType.ANY

    # change testing data
    invitem = inventoryData[1].split("¦")
    invitem[0] = str(uuid4())
    invitem[2] = f"{invitem[2]} new"
    addInvData("¦".join(invitem))

    # data in chache is not changed
    inventory = asyncio.run(ls.inventoryGet())
    assert len(inventory.items) == 4
    assert inventory.filtered == InvetoryType.ANY

    # drop inventory from cache
    resp = httpx.post(
        f"{http_service}/lsl/changed?change={Change.INVENTORY}",
        headers=headers | {"X-Auth-Token": auth_token},
    )
    assert resp.status_code == 200
    inventory = asyncio.run(ls.inventoryGet())
    assert len(inventory.items) == 5
    assert inventory.filtered == InvetoryType.ANY

    inventory = asyncio.run(ls.inventoryGet(InvetoryType.NOTECARD))
    assert len(inventory.items) == 2
    assert inventory.filtered == InvetoryType.NOTECARD

    inventory = asyncio.run(ls.inventoryGet(InvetoryType.SCRIPT))
    assert len(inventory.items) == 1
    assert inventory.filtered == InvetoryType.SCRIPT

    inventory = asyncio.run(ls.inventoryGet(InvetoryType.SOUND))
    assert len(inventory.items) == 0
    assert inventory.filtered == InvetoryType.SOUND

    # without auth token
    resp = httpx.post(
        f"{http_service}/lsl/changed?change={Change.INVENTORY}",
        headers=headers,
    )
    assert resp.status_code == 403

    # invalid shard
    hdrsAuth = headers | {"x-secondlife-shard": "Testing"}
    resp = httpx.post(
        f"{http_service}/lsl/changed?change={Change.INVENTORY}",
        headers=hdrsAuth,
    )
    assert resp.status_code == 403

    # invalid auth token
    token = sha512(randbits(512).to_bytes(64, "big")).hexdigest()
    setAuthToken(token)
    with pytest.raises(HTTPForbidden):
        inventory = asyncio.run(ls.inventoryGet())
    setAuthToken(auth_token)
