from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import VersionProperty, ExpressionProperty
from .broker import RequestResponseBroker


@Discoverable(DiscoverableType.block)
class WebOutput(Block):

    version = VersionProperty('1.0.0')

    id_val = ExpressionProperty(title='Request ID', default='{{ $id }}')

    response_out = ExpressionProperty(title='Response Body', defualt='')
    response_status = ExpressionProperty(
        title='Response Status', defualt='200')

    def process_signals(self, signals, input_id='default'):
        for sig in signals:
            try:
                req_id = self.id_val(sig)
                rsp_body = self.response_out(sig)
                rsp_status = int(self.response_status(sig))
            except:
                self._logger.exception("Unable to build response")
                continue

            self._logger.debug(
                "Writing response for request ID {}".format(req_id))
            RequestResponseBroker.write_response(
                req_id,
                body=rsp_body,
                status=rsp_status)
