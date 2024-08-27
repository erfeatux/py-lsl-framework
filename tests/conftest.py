from secrets import randbits
from hashlib import sha512

# import logging
import pytest
import httpx
import os

from lslframework.config.config import AppSettings

from tests.fakes.http import setAuthToken


def is_responsive(url):
    try:
        resp = httpx.get(url)
        if resp.status_code == 404:
            return True
    except httpx.ReadError:
        return False
    except httpx.RemoteProtocolError:
        return False
    except httpx.ReadTimeout:
        return False
    return False


@pytest.fixture(scope="session")
def headers() -> dict[str, str]:
    return {
        "X-SecondLife-Owner-Key": "00000000-0000-0000-0000-000000000000",
        "X-SecondLife-Owner-Name": "nickname",
        "X-SecondLife-Object-Key": "00000000-0000-0000-0000-000000000000",
        "X-SecondLife-Object-Name": "Test obj name",
        "X-SecondLife-Local-Position": "(50.362698, 39.342766, 1000.523254)",
        "X-SecondLife-Local-Rotation": "(0.0, 0.0, 0.0, 1.0)",
        "X-SecondLife-Local-Velocity": "(0.0, 0.0, 0.0)",
        "X-SecondLife-Region": "Region Name (256, 512)",
        "X-SecondLife-Shard": "Production",
    }


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "docker", "docker-compose.yml")


@pytest.fixture(scope="session")
def docker_setup():
    return ["--env-file .env up --build -d"]


@pytest.fixture(scope="session")
def http_service(docker_ip, docker_services):
    """Ensure that HTTP service is up and responsive."""

    # logLevel = logging.root.level
    # logging.root.level = 50

    cfg = AppSettings()
    url = f"http://{docker_ip}:{cfg.HTTP_PORT}"
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    # logging.root.level = logLevel
    return url


@pytest.fixture(scope="session")
def auth_token(http_service, headers) -> str:
    cfg = AppSettings()
    randstring = sha512(randbits(512).to_bytes(64, "big")).hexdigest()
    calc = sha512(randstring.encode("UTF-8"))
    calc.update(cfg.token.encode("UTF-8"))
    sign = calc.hexdigest()
    resp = httpx.post(
        f"{http_service}/lsl/auth?sign={sign}",
        headers=headers,
        content=randstring,
    )
    if resp.status_code != 200:
        raise ValueError(f"Can't get auth token: {resp.status_code=}")
    token = resp.read().decode("UTF-8")
    setAuthToken(token)
    return token
