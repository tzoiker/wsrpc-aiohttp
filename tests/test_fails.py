from aiohttp import ClientConnectionError
from wsrpc_aiohttp.testing import BaseTestCase, async_timeout


class TestDisconnect(BaseTestCase):
    @async_timeout
    async def test_call_error(self):
        class DataStore:
            def get_data(self, _):
                return 1000

        self.WebSocketHandler.add_route('get_data', DataStore().get_data)

        client = await self.get_ws_client()

        # Imitation of server connection has been closed
        client.socket._closed = True

        with self.assertRaises(ClientConnectionError):
            await client.call('get_data')
