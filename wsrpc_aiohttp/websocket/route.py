import logging

import asyncio
from abc import ABC, abstractmethod

from . import handler       # noqa

log = logging.getLogger("wsrpc")


class decorators(object):
    _NOPROXY = set([])
    _PROXY_ATTR = '__wsrpc_aiohttp_proxy__'

    @staticmethod
    def noproxy(func):
        decorators._NOPROXY.add(func)
        return func

    @staticmethod
    def proxy(f):
        setattr(f, decorators._PROXY_ATTR, True)
        return f

    @staticmethod
    def proxied(f):
        return getattr(f, decorators._PROXY_ATTR, False)


class AbstractRoute(ABC):

    def __init__(self, obj: 'handler.WebSocketBase'):
        self.socket = obj

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self.socket._loop  # noqa

    def _onclose(self):
        pass

    @abstractmethod
    def proxy(self, method):
        raise NotImplementedError

    def _resolve(self, method):
        if method.startswith('_'):
            raise AttributeError('Trying to get private method.')

        if hasattr(self, method) and self.proxy(method):
            return getattr(self, method)
        else:
            raise NotImplementedError('Method not implemented')


class Route(AbstractRoute):

    @abstractmethod
    def proxy(self, method):
        func = getattr(self, method)
        return decorators.proxied(func)

    @decorators.proxy
    def placebo(self, *args, **kwargs):
        log.debug("PLACEBO IS CALLED!!! args: %r, kwargs: %r", args, kwargs)


class LegacyRoute(Route):
    _NOPROXY = []

    @classmethod
    def noproxy(cls, func):
        def wrap(*args, **kwargs):
            if func not in cls._NOPROXY:
                cls._NOPROXY.append(func)
                wrap(*args, **kwargs)

            return func(*args, **kwargs)
        return wrap

    @abstractmethod
    def proxy(self, method):
        func = getattr(self, method)
        return not (func in decorators._NOPROXY)


WebSocketRoute = LegacyRoute


__all__ = (
    'AbstractRoute', 'Route',
    'WebSocketRoute', 'LegacyRoute', 'decorators',
)
