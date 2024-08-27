from dependency_injector import containers, providers

# rediscache - default cache implementation
from .rediscache import Cache


class Container(containers.DeclarativeContainer):
    cache = providers.Singleton(Cache)
