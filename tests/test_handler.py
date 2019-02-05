from collections import defaultdict
from unittest.mock import MagicMock
from nio.testing.block_test_case import NIOBlockTestCase
from ..handler import Handler
from ..web_handler_block import WebHandler


class TestHandler(NIOBlockTestCase):

    def test_handler_post(self):
        handler = Handler(endpoint='', blk=MagicMock(spec=WebHandler()))
        handler.run_request = MagicMock()
        handler.on_post(MagicMock(), MagicMock())
        self.assertEqual(handler.run_request.call_args[0][0], 'POST')

    def test_handler_options(self):
        handler = Handler(endpoint='', blk=MagicMock(spec=WebHandler()))
        handler.on_options(MagicMock(), MagicMock())

    def test_handler_headers(self):
        """ Handler should add optional headers to all request types """
        headers = {
            "Access-Control-Allow-Origin": "https://app.local:3000"
        }

        handler = Handler(endpoint='',
                          blk=MagicMock(spec=WebHandler()),
                          headers=headers)

        handler.run_request = MagicMock()

        for method in ['on_get','on_post','on_put','on_delete','on_options']:
            resp=MagicMock()
            getattr(handler, method)(MagicMock(), resp)
            self.assertEqual(resp.set_header.call_args[0],
                            ('Access-Control-Allow-Origin', 'https://app.local:3000'))
