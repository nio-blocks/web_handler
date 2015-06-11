from uuid import uuid4
from .broker import RequestResponseBroker
from nio.common.signal.base import Signal
from nio.modules.web import RESTHandler


class Handler(RESTHandler):

    def __init__(self, endpoint, blk):
        super().__init__('/' + endpoint)
        self._blk = blk
        self._logger = blk._logger

    def on_post(self, req, rsp):

        request_id = uuid4()
        out_sig = Signal({
            'id': request_id,
            'body': req.get_body(),
            'method': 'POST'
        })

        self._blk.notify_signals([out_sig])

        RequestResponseBroker.register_request(
            request_id, req, rsp, self._blk.get_timeout_seconds())
