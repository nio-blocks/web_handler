from collections import defaultdict
from unittest.mock import MagicMock
from nio.testing.block_test_case import NIOBlockTestCase
from ..handler import Handler


class TestHandler(NIOBlockTestCase):

    def test_handler_post(self):
        handler = Handler(endpoint='', blk=MagicMock())
        handler.run_request = MagicMock()
        handler.on_post(MagicMock(), MagicMock())
        self.assertEqual(handler.run_request.call_args[0][0], 'POST')

    def test_handler_options(self):
        handler = Handler(endpoint='', blk=MagicMock())
        handler.on_options(MagicMock(), MagicMock())
