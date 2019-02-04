import json
from uuid import uuid4
from .broker import RequestResponseBroker
from nio.signal.base import Signal
from nio.modules.web import RESTHandler


class Handler(RESTHandler):

    """ A REST Handler that will listen for HTTP requests and register them """

    def __init__(self, endpoint, blk, headers=None):
        super().__init__('/' + endpoint)
        self._blk = blk
        self.logger = blk.logger
        self._headers = headers

    def on_get(self, req, rsp):
        self.__add_headers(rsp)
        self.run_request('GET', req, rsp, include_body=False)

    def on_post(self, req, rsp):
        self.__add_headers(rsp)
        self.run_request('POST', req, rsp, include_body=True)

    def on_put(self, req, rsp):
        self.__add_headers(rsp)
        self.run_request('PUT', req, rsp, include_body=True)

    def on_delete(self, req, rsp):
        self.__add_headers(rsp)
        self.run_request('DELETE', req, rsp, include_body=False)

    def on_options(self, req, rsp):
        self.__add_headers(rsp)

    def run_request(self, method, req, rsp, include_body=False):
        """ Record an HTTP request for a given method """
        # Make sure this method is supported by the block
        self.logger.debug(
            "Received {} request, validating method".format(method))
        if not self.validate_method(method, rsp):
            return

        # Generate a unique ID for this request
        request_id = uuid4()

        # Register this request with the broker
        self.logger.debug(
            "Registering request with request ID {}".format(request_id))
        RequestResponseBroker.register_request(
            request_id, req, rsp, self._blk.get_timeout_seconds())

        # Next, notify the signal containing the request information
        self.logger.debug(
            "Notifiying request signal with request ID {}".format(request_id))
        try:
            self._blk.notify_signals([self.build_output_signal(
                request_id, req, method, include_body)])
        except:
            self.logger.exception("Unable to build signal for request")
            raise

        # Wait for the response to be written, this call will block until
        # the resposne is written to or the timeout occurs
        RequestResponseBroker.wait_for_response(request_id)

    def build_output_signal(self, request_id, req_obj,
                            http_method, include_body):
        out_sig = Signal({
            'id': request_id,
            'method': http_method,
            'params': req_obj.get_params(),
            'headers': req_obj._headers,
        })

        if include_body:
            try:
                setattr(out_sig, 'body', self.get_body_for_signal(req_obj))
            except:
                self.logger.exception("Unable to get request body")
                raise
        return out_sig

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

    def __add_headers(self, rsp):
        if self._headers is not None:
            for header in self._headers:
                rsp.set_header(header, self._headers[header])

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

    def build_output_signal(self, request_id, req_obj,
                            http_method, include_body):
        """ For the JSON Handler, return the body as the body of the signal """
        self.logger.debug("Building output signal")
        req_info = {
            '_id': request_id,
            '_method': http_method,
            '_params': req_obj.get_params(),
            '_headers': req_obj._headers,
        }

        try:
            if include_body:
                req_body = self.get_body_for_signal(req_obj)
            else:
                req_body = {}
        except:
            self.logger.exception("Unable to get request body")
            raise

        if not isinstance(req_body, dict):
            raise TypeError("The request body must be a dictionary")

        req_body.update(req_info)

        return Signal(req_body)
