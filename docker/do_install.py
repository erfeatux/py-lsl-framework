#!/bin/env python3

import os
import dotenv
import shutil
from types import GetSetDescriptorType

from pydantic_core import Url
from pydantic_settings import BaseSettings

from lslframework.config import cfg


def writeENV(cfg: BaseSettings, **values):
    for k, v in values.items():
        cfg.validate({k: v})
        dotenv.set_key(str(cfg.model_config["env_file"]), k, str(v))
        setattr(cfg, k, v)


def updateUrl(url: Url, **kwargs) -> Url:
    if not len(kwargs):
        raise ValueError("Nothing to update")
    argnames = [k for k, v in vars(Url).items() if isinstance(v, GetSetDescriptorType)]
    invalid_args = {k: v for k, v in kwargs.items() if k not in argnames}
    if len(invalid_args):
        raise ValueError(f"Invalid named args: {invalid_args}")

    ret = {k: getattr(url, k) for k in dir(url) if k in argnames}
    ret.update(kwargs)
    return Url.build(**ret)


if os.environ.get("runtime", "testing").lower() == "production":
    shutil.rmtree("tests/")

writeENV(
    cfg.redis,
    connectionTestShard=updateUrl(
        cfg.redis.connectionTestShard, port=6379, host="redis"
    ),
)

writeENV(
    cfg.redis,
    connectionProdShard=updateUrl(
        cfg.redis.connectionProdShard, port=6379, host="redis"
    ),
)
