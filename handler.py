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
            setattr(out_sig, 'body', req.get_body())

        request_lock = RequestResponseBroker.get_lock(request_id)
        request_lock.acquire()
        self._logger.debug(
            "Notifiying request signal with request ID {}".format(request_id))
        self._blk.notify_signals([out_sig])

        # Register this request with the broker, this call will block until
        # the resposne is written to or the timeout occurs
        RequestResponseBroker.register_request(
            request_id, req, rsp, self._blk.get_timeout_seconds())

        # The lock should be released by now, but in case it's not we'll
        # safely reacquire and then release
        request_lock.acquire(False)
        request_lock.release()

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
