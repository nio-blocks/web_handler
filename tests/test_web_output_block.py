from unittest.mock import patch
from ..broker import RequestResponseBroker
from collections import defaultdict
from ..web_output_block import WebOutput
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase


class TestWebOutput(NIOBlockTestCase):

    def test_writes_response(self):
        """ Test that the block writes responses, this is the default """
        blk = WebOutput()
        self.configure_block(blk, {
            'response_out': '{{ $body }}',
            'id_val': '{{ $id }}',
            'response_status': '{{ $status }}',
            'response_headers': [{
                'header_name': '{{ $header["name"] }}',
                'header_val': '{{ $header["value"] }}'
            }]
        })
        headers = {'HEADER_NAME': 'HEADER_VALUE'}
        test_sig = Signal({
            'body': 'test body',
            'status': '201',  # String version of status, should cast
            'id': 'fakeid',
            'header': {'name': 'HEADER_NAME', 'value': 'HEADER_VALUE'}
        })
        with patch.object(RequestResponseBroker, 'write_response') as write:
            blk.process_signals([test_sig])
            write.assert_called_once_with(
                'fakeid', body='test body', headers=headers, status=201)

    def test_bad_status(self):
        """ Test that the block does not write on a bad status """
        blk = WebOutput()
        self.configure_block(blk, {
            'response_status': '{{ $status }}'
        })
        test_sig = Signal({
            'status': 'notanumber'
        })
        with patch.object(RequestResponseBroker, 'write_response') as write:
            blk.process_signals([test_sig])
            self.assertEqual(write.call_count, 0)
