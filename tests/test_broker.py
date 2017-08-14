from unittest.mock import MagicMock

from uuid import uuid4
from time import sleep

from nio.util.threading.spawn import spawn
from nio.modules.web.request import Request
from nio.modules.web.response import Response
from nio.testing.block_test_case import NIOBlockTestCase

from ..broker import RequestResponseBroker


class TestBroker(NIOBlockTestCase):

    def get_test_modules(self):
        """ Adds 'web' and 'security' to default modules """
        return super().get_test_modules() | {'web'}

    def setUp(self):
        super().setUp()
        RequestResponseBroker._mappings.clear()

    def test_writes_response(self):
        """ Tests that the broker writes to the proper response """

        req_id, mock_rsp = self.register_request(5)
        sleep(1)
        RequestResponseBroker.write_response(
            req_id, status=123, body='body',
            headers={'header_name': 'header_value'})

        mock_rsp.set_body.assert_called_once_with('body')
        mock_rsp.set_status.assert_called_once_with(123)

        # Give the event some time to trigger, make sure it got cleaned up
        sleep(0.1)
        self.assertEqual(RequestResponseBroker._mappings, {})

    def test_timeout(self):
        """ Tests that the broker times out if not written in time """

        # make a request with timeout 1s, but wait 2s
        req_id, mock_rsp = self.register_request(1)
        sleep(2)

        # Make sure we got the timeout error code
        mock_rsp.set_status.assert_called_once_with(504)

        with self.assertRaises(ValueError):
            RequestResponseBroker.write_response(
                req_id, status=123, body='body',
                headers={'header_name': 'header_value'})

    def get_mocked_request(self):
        req = Request()
        return req

    def get_mocked_response(self):
        rsp = Response()
        rsp.set_body = MagicMock()
        rsp.set_status = MagicMock()
        rsp.set_header = MagicMock()
        return rsp

    def register_request(self, timeout):
        """ Register a request in a new thread and return the ID and resp """
        req_id = uuid4()
        mock_rsp = self.get_mocked_response()
        mock_req = self.get_mocked_request()
        RequestResponseBroker.register_request(
            req_id, mock_req, mock_rsp, timeout)
        spawn(RequestResponseBroker.wait_for_response, req_id)
        return req_id, mock_rsp
