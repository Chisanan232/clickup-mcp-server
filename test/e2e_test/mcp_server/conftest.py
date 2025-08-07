from abc import abstractmethod, ABCMeta
from typing import Type, AsyncGenerator

import pytest
from .base.client import SSEClient, StreamingHTTPClient, EndpointClient


class MCPClientFixture(metaclass=ABCMeta):
    @property
    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError

    @pytest.fixture(params=[SSEClient, StreamingHTTPClient], ids=["sse", "streaming-http"])
    async def client(self, request: pytest.FixtureRequest) -> AsyncGenerator[EndpointClient, None]:
        cls: Type[EndpointClient] = request.param
        c = cls(url=self.url)
        await c.connect()
        yield c
        await c.close()
