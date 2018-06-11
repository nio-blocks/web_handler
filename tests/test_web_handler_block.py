from unittest.mock import MagicMock, patch
from collections import defaultdict
from ..web_handler_block import WebHandler
from ..handler import Handler
from nio.testing.block_test_case import NIOBlockTestCase


class TestWebHandler(NIOBlockTestCase):

    def get_test_modules(self):
        """ Adds 'web' and 'security' to default modules """
        return super().get_test_modules() | {'web'}

    def test_block_api(self):
        """ Test that the block provides the correct values for the API """
        with patch(WebHandler.__module__ + ".WebEngine") as mock_web_engine:
            blk = WebHandler()
            self.configure_block(blk, {
                'request_timeout': {'seconds': 7},
                'port': '1234',  # make sure giving a string works too
                'host': 'fakehost'
            })
        self.assertEqual(blk.get_timeout_seconds(), 7)
        self.assertEqual(mock_web_engine.add_server.call_count, 1)
        # String passed to block, int passed to configure
        self.assertEqual(mock_web_engine.add_server.call_args[0][0], 1234)
        self.assertEqual(mock_web_engine.add_server.call_args[0][1],
                         "fakehost")
        # TODO: These all return True now, update when support for
        # different methods is available
        self.assertTrue(blk.supports_method('GET'))
        self.assertTrue(blk.supports_method('POST'))
        self.assertTrue(blk.supports_method('PUT'))
        self.assertTrue(blk.supports_method('DELETE'))
        self.assertTrue(blk.supports_method('NOTAMETHOD'))
        self.assertTrue(blk.supports_method('OPTIONS'))

    def test_override_auth(self):
        """ Optionally disable authentication """
        with patch(WebHandler.__module__ + ".WebEngine") as mock_web_engine:
            blk = WebHandler()
            self.configure_block(blk, {
                'auth': False
            })
        self.assertEqual(Handler.before_handler, blk._no_auth)
