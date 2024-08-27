# this module contains the http request mechanism
# fake for unit tests

from logging import getLogger
from uuid import uuid4
from typing import Any
import re

from lslgwclient.client.basehttp import HTTP as BaseHTTP
from lslgwclient.client.basehttp import ClientResponse as BaseClientResponse

creatorId = uuid4()
log = getLogger(__name__)

authToken: str | None = None


def setAuthToken(token: str) -> None:
    global authToken
    authToken = token


# data
inventoryData = [
    "fd42e87a-44d8-1343-9ecd-fc7dd23f6765¦7¦A&Y_Re-delivery_issue"
    + "¦2023-03-03 21:17:52 note card¦bf1d107f-2c7a-4e0b-9cac-d2b30ccd2821"
    + "¦581632¦581632¦0¦0¦581632¦2024-08-07T00:32:31Z",
    "488c4978-99e3-449a-4c98-5fc221e5a7a5¦0¦A&Y_logo¦(No Description)"
    + "¦0c2566cd-2ac9-4566-bab4-a3c4bfce58bd¦581632¦581632¦0¦0¦581632¦2024-08-07T00:32:43Z",
    "0c13f3e7-7d41-5675-ee70-fa9309319f07¦7¦New Note¦2022-05-30 19:59:13 note card"
    + "¦07ce6a4a-b34e-4e62-96e3-16f2a8b19c89¦2147483647¦2147483647"
    + "¦0¦0¦581632¦2024-08-07T00:32:31Z",
    "00cc5bf5-2e03-8cfa-3c36-fc5b40238d7f¦10¦New Script¦2024-08-07 03:42:12 lsl2 script"
    + "¦07ce6a4a-b34e-4e62-96e3-16f2a8b19c89¦2147483647¦2147483647"
    + "¦0¦0¦532480¦2024-08-06T23:42:12Z",
]


def addInvData(line: str) -> None:
    inventoryData.append(line)


class ClientResponse(BaseClientResponse):
    __text: str
    __status: int
    __reason: str | None
    headers: dict[str, str] = {
        "Date": "Sat, 27 Jul 2024 22:38:52 GMT",
        "Server": "Second Life LSL/Second Life Server 2024-06-11.9458617693 (http://secondlife.com)",
        "X-LL-Request-Id": "ZqV2_NCg1ZQVEy3NK2hjeQAAA40",
        "Content-Length": "205",
        "Cache-Control": "no-cache, max-age=0",
        "Content-Type": "text/plain; charset=utf-8",
        "Pragma": "no-cache",
        "X-SecondLife-Local-Position": "(50.362698, 39.342766, 1000.523254)",
        "X-SecondLife-Local-Rotation": "(0.000000, 0.000000, 0.000000, 1.000000)",
        "X-SecondLife-Local-Velocity": "(0.000000, 0.000000, 0.000000)",
        "X-SecondLife-Object-Key": "00000000-0000-0000-0000-000000000000",
        "X-SecondLife-Object-Name": "Test object name",
        "X-SecondLife-Owner-Key": "00000000-0000-0000-0000-000000000000",
        "X-SecondLife-Owner-Name": "FName LName",
        "X-SecondLife-Region": "Region Name (256, 512)",
        "X-SecondLife-Shard": "Production",
        "Access-Control-Allow-Origin": "*",
        "Connection": "close",
    }

    def __init__(self, text: str, status: int = 200, reason: str | None = None) -> None:
        self.__text = text
        self.__status = status
        self.__reason = reason

    async def text(self) -> str:
        return self.__text

    @property
    def status(self) -> int:
        return self.__status

    @property
    def reason(self) -> str | None:
        return self.__reason


class HTTP(BaseHTTP):
    # http get method
    @staticmethod
    async def get(url: str, headers: dict[str, Any] = dict()) -> ClientResponse:
        log.debug(f"{url=}, {headers=}")
        if not len(headers) or not authToken or headers["X-Auth-Token"] != authToken:
            log.warning(f"Invalid auth token: {authToken} {url=}, {headers=}")
            raise await HTTP.__exceptionByResp(ClientResponse("err", status=403))
        match url.lower():
            case url if "/inventory/read?type=-1" in url:
                return ClientResponse("\n".join(inventoryData))
            case url if "/inventory/read?type=" in url:
                types = re.findall(r"\d+$", url)
                if (
                    not isinstance(types, list)
                    or len(types) != 1
                    or not types[0].isdigit()
                ):
                    raise await HTTP.__exceptionByResp(
                        ClientResponse("err", status=422)
                    )

                return ClientResponse(
                    "\n".join(
                        list(
                            filter(
                                lambda x: int(x.split("¦")[1]) == int(types[0]),
                                inventoryData,
                            )
                        )
                    )
                )

        return ClientResponse("")

    # http get method
    @staticmethod
    async def post(
        url: str, data: str | None, headers: dict[str, Any] = dict()
    ) -> ClientResponse:
        log.debug(f"{url=}; {data=}")

        return ClientResponse("")
