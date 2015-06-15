from mock import MagicMock
from collections import defaultdict
from ..web_handler_block import WebHandler
from nio.util.support.block_test_case import NIOBlockTestCase


class TestWebHandler(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        # This will keep a list of signals notified for each output
        self.last_notified = defaultdict(list)

    def signals_notified(self, signals, output_id='default'):
        self.last_notified[output_id].extend(signals)

    def test_block_api(self):
        """ Test that the block provides the correct values for the API """
        blk = WebHandler()
        blk.configure_server = MagicMock()
        self.configure_block(blk, {
            'request_timeout': {'seconds': 7},
            'port': '1234',  # make sure giving a string works too
            'host': 'fakehost'
        })

        self.assertEqual(blk.get_timeout_seconds(), 7)

        self.assertEqual(blk.configure_server.call_count, 1)
        self.assertEqual(blk.configure_server.call_args[0][0], {
            'host': 'fakehost',
            'port': 1234  # String passed to block, int passed to configure
        })

        # TODO: These all return True now, update when support for
        # different methods is available
        self.assertTrue(blk.supports_method('GET'))
        self.assertTrue(blk.supports_method('POST'))
        self.assertTrue(blk.supports_method('PUT'))
        self.assertTrue(blk.supports_method('DELETE'))
        self.assertTrue(blk.supports_method('NOTAMETHOD'))
