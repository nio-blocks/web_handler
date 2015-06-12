import json
from uuid import uuid4
from .broker import RequestResponseBroker
from nio.common.signal.base import Signal
from nio.modules.web import RESTHandler


class Handler(RESTHandler):

    """ A REST Handler that will listen for HTTP requests and register them """

    def __init__(self, endpoint, blk):
        super().__init__('/' + endpoint)
        self._blk = blk
        self._logger = blk._logger

    def on_get(self, req, rsp):
        self.run_request('GET', req, rsp, include_body=False)

    def on_post(self, req, rsp):
        self.run_request('POST', req, rsp, include_body=True)

    def on_put(self, req, rsp):
        self.run_request('PUT', req, rsp, include_body=True)

    def on_delete(self, req, rsp):
        self.run_request('DELETE', req, rsp, include_body=False)

    def run_request(self, method, req, rsp, include_body=False):
        """ Record an HTTP request for a given method """
        # Make sure this method is supported by the block
        self._logger.debug(
            "Received {} request, validating method".format(method))
        if not self.validate_method(method, rsp):
            return

        # Generate a unique ID for this request
        request_id = uuid4()
        out_sig = Signal({
            'id': request_id,
            'method': method,
            'params': req.get_params(),
            'headers': req._headers
        })

        if include_body:
            try:
                setattr(out_sig, 'body', self.get_body_for_signal(req))
            except:
                self._logger.exception("Unable to get request body")
                raise

        self._logger.debug(
            "Registering request with request ID {}".format(request_id))
        # Register this request with the broker
        RequestResponseBroker.register_request(
            request_id, req, rsp, self._blk.get_timeout_seconds())

        self._logger.debug(
            "Notifiying request signal with request ID {}".format(request_id))
        self._blk.notify_signals([out_sig])

        # Wait for the response to be written, this call will block until
        # the resposne is written to or the timeout occurs
        RequestResponseBroker.wait_for_response(request_id)

    def get_body_for_signal(self, req):
        """ Get the body to store on the signal """
        return req.get_body()

    def validate_method(self, method, rsp):
        """ Make sure the HTTP method is supported by the block.

        If it is not, write a 501 to the response and return False

        Returns:
            success (bool): True if the method is supported, False if not
        """
        if self._blk.supports_method(method):
            return True

        rsp.set_status(501)
        return False

class JSONHandler(Handler):

    def get_body_for_signal(self, req):
        """ Parse the JSON of the body rather than use a string.

        Raises:
            ValueError: If the body does not contain valid JSON
        """
        req_body = req.get_body()
        if not (isinstance(req_body, list) or isinstance(req_body, dict)):
            return json.loads(req_body)
        return req_body
