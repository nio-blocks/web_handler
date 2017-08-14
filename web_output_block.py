import json

from nio.block.base import Block
from nio.properties import VersionProperty, Property, \
    PropertyHolder, ListProperty, IntProperty

from .broker import RequestResponseBroker


class ResponseHeader(PropertyHolder):
    header_name = Property(title='Name', default='Content-Type')
    header_val = Property(title='Value', default='application/json')


class WebOutput(Block):

    version = VersionProperty('1.0.0')
    id_val = Property(title='Request ID', default='{{ $id }}')
    response_out = Property(title='Response Body', default='')
    response_status = IntProperty(
        title='Response Status', default=200)
    response_headers = ListProperty(ResponseHeader, title='Response Headers',
                                    default=[])

    def process_signals(self, signals, input_id='default'):
        for sig in signals:
            try:
                req_id = self.id_val(sig)
                rsp_body = self.build_body(sig)
                rsp_status = self.response_status(sig)
                rsp_headers = self.build_headers(sig)
            except:
                self.logger.exception("Unable to build response")
                continue

            try:
                self.put_response(req_id, rsp_body, rsp_headers, rsp_status)
            except:
                self.logger.exception("Unable to write response")

    def build_headers(self, signal):
        """ Determine the headers of the response given an input signal """
        return {
            header.header_name(signal): header.header_val(signal)
            for header in self.response_headers()
        }

    def build_body(self, signal):
        """ Determine the body of the response given an input signal """
        return self.response_out(signal)

    def put_response(self, req_id, body, headers, status):
        """ For a given request ID, write a response.

        Args:
            req_id: A request ID - should be taken from the WebHandler block
            body: What to include in the response body, None or '' for no body
            headers (dict): A dictionary containing the response headers to set
            status (int): The HTTP response status code

        Returns:
            None
        """
        self.logger.debug(
            "Writing response for request ID {}".format(req_id))
        RequestResponseBroker.write_response(
            req_id, body=body, headers=headers, status=status)


class WebJSONOutput(WebOutput):

    """ An output block that writes JSON data to the response.

    The block will JSON encode the body and set the proper application/json
    Content-Type header.

    """
    # The JSON block will assume the ID is in a hidden field and that the
    # body of the response is just the (non-hidden) contents of the signal
    id_val = Property(title='Request ID', default='{{ $_id }}')
    response_out = Property(
        title='Response Body',
        default='{{ json.dumps($to_dict(), default=str) }}')
    version = VersionProperty("1.0.0")

    def build_body(self, signal):
        resp_obj = self.response_out(signal)
        if not isinstance(resp_obj, str):
            resp_obj = json.dumps(resp_obj)
        return resp_obj

    def build_headers(self, signal):
        """ Determine the headers of the response given an input signal """
        configured_headers = super().build_headers(signal)
        if 'Content-Type' not in configured_headers:
            configured_headers['Content-Type'] = 'application/json'

        return configured_headers
