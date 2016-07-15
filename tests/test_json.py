import json
import requests
from collections import defaultdict
from ..broker import RequestResponseBroker
from ..web_handler_block import WebJSONHandler
from ..web_output_block import WebJSONOutput
from unittest.mock import patch
from nio.testing.block_test_case import NIOBlockTestCase
from nioext.util.support import NIOExtModuleLocations
from nioext.util.support.provider import NIOExtTestConfigurationProvider


class TestJSONRequests(NIOBlockTestCase):

    def get_test_modules(self):
        return super().get_test_modules() + ['web']

    def get_module_locations(self):
        return NIOExtModuleLocations

    def get_test_configuration_provider(self):
        return NIOExtTestConfigurationProvider

    def setUp(self):
        super().setUp()
        self.last_notified = defaultdict(list)
        # Build the handler and output blocks
        self.handler_block = WebJSONHandler()
        self.configure_block(self.handler_block, {
            'host': '127.0.0.1',
            'port': 8182
        })

        self.output_block = WebJSONOutput()
        self.configure_block(self.output_block, {
            'response_status': '200'
        })

        self.output_block.start()
        self.handler_block.start()

    def tearDown(self):
        self.output_block.stop()
        self.handler_block.stop()
        super().tearDown()

    def signals_notified(self, signals, output_id='default'):
        self.last_notified[output_id].extend(signals)

    def make_request(self, method='GET', body=None):
        url = 'http://127.0.0.1:8182'
        if body:
            return requests.request(method, url, data=body)
        else:
            return requests.request(method, url)

    def test_basic_json(self):
        """ Make sure that a basic chain of handler to output works """

        json_obj = {
            "json_key": {
                "nested": "value"
            }
        }
        # Start by patching the register in the broker, and making a request
        with patch.object(RequestResponseBroker, 'wait_for_response') as reg:
            self.make_request('POST', json.dumps(json_obj))
            # Make sure our request was registered and that a signal
            # was notified
            self.assertEqual(reg.call_count, 1)
            self.assert_num_signals_notified(1, self.handler_block)

        the_sig = self.last_notified['default'][0]
        # Make sure the signal's body came through as an actual dictionary
        # and not a string due to the JSON handler being used
        self.assertDictEqual(the_sig.json_key, {"nested": "value"})

        # Now patch the write response
        with patch.object(RequestResponseBroker, 'write_response') as write:
            # Forward the output signal from the handler to the output
            self.output_block.process_signals([the_sig])

            # Make sure write_response was called with the correct ID
            self.assertEqual(write.call_count, 1)
            self.assertEqual(write.call_args[0][0], the_sig._id)
            self.assertDictEqual(
                json.loads(write.call_args[1]['body']), json_obj)
            self.assertEqual(
                write.call_args[1]['headers']['Content-Type'],
                'application/json')

    def test_bad_json_request(self):
        """Make sure that bad JSON request doesn't make through the handler"""
        with patch.object(RequestResponseBroker, 'wait_for_response') as reg:
            self.make_request('POST', 'string not JSON')
            # Make sure our request was registered and that a signal
            # was notified
            self.assertEqual(reg.call_count, 0)
