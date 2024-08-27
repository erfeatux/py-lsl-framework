from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, RedisDsn
from enum import Enum
import re


class LogLevel(Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class Runtime(Enum):
    production = "production"
    testing = "testing"


class SLShard(Enum):
    production = "Production"  # Agni
    testing = "Testing"  #       Aditi


class AppSettings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    runtime: Runtime = Runtime.testing
    """runtime type: production or testing"""
    logLevel: LogLevel = LogLevel.debug
    token: str = Field(pattern=re.compile(r"[0-9a-f]{128}"))
    """LSL application secret auth token"""
    shards: list[SLShard] = [SLShard.production, SLShard.testing]
    """SL shards allowed to use"""
    REDIS_PORT: int = Field(ge=0, le=65535, default=63799)
    """External redis port"""
    HTTP_PORT: int = Field(ge=0, le=65535, default=8080)
    """External http port"""


class RedisSettings(BaseSettings):
    """Redis connection settings"""

    model_config = SettingsConfigDict(
        env_file=".redis.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="forbid",
    )

    connectionProdShard: RedisDsn = RedisDsn("redis://localhost/0")
    """Redis connection url for production shard (Agni)"""
    connectionTestShard: RedisDsn = RedisDsn("redis://localhost/1")
    """Redis connection url for testing shard (Aditi)"""


class Config:
    app = AppSettings()
    redis = RedisSettings()
