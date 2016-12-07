from threading import Event


class RequestResponseBroker(object):

    _mappings = {}

    @classmethod
    def register_request(cls, id, req, rsp, timeout):
        """ Register that a request has occurred by saving the relevant info


        Args:
            id: A unique identifier for this request. This same ID should be
                passed when the response is written
            req: The original nio.modules.web.http.Request object
            rsp: The nio.modules.web.http.Response object to write to
            timeout (float): The total number of seconds to wait for a response
                to be written. If a response is not written in this amount
                of time, a timeout error will be returned instead

        Returns:
            None
        """
        req_event = Event()
        cls._mappings[id] = {
            'req': req,
            'rsp': rsp,
            'timeout': timeout,
            'event': req_event
        }

    @classmethod
    def wait_for_response(cls, req_id):
        """ Wait for a response for a given request ID

        Note, this method will block the current thread until the response
        is written or the timeout has occurred.

        Returns:
            None
        """
        request_info = cls.get_request_info(req_id)

        # Wait for this request's event to be set by a response writer
        if not request_info['event'].wait(request_info['timeout']):
            # We timed out, write an error to the response
            cls.write_timeout_error(request_info['rsp'])

        # We're done with this ID, clean it up from the mappings
        del cls._mappings[req_id]

    @classmethod
    def get_request_info(cls, id):
        """ Get the request info for a given request ID.

        Returns:
            info (dict): The saved information about the request

        Raises:
            ValueError: If the ID is invalid or already timed out
        """
        if id not in cls._mappings:
            raise ValueError("The request ID {} has not been "
                             "registered or has timed out".format(id))

        return cls._mappings[id]

    @classmethod
    def write_timeout_error(cls, rsp):
        """ Build a response indicating that the request timed out """
        rsp.set_status(504)
        rsp.set_body("The service did not respond in time")

    @classmethod
    def write_response(cls, id, status=200, body=None, headers=None):
        """ Write to the saved response object for a given request ID.

        This method will look up the cached response information, write to it,
        and set the event indicating to the original thread that the response
        is ready to be returned.

        Args:
            id: The same ID of the original request
            status (int): The HTTP status to return - 200 by default
            body (str, bytes): The body of the response to return. None or ''
                for no body on the response at all
            headers (dict): Dictionary containing response headers

        Raises:
            ValueError: If the ID is invalid or already timed out
        """
        request_info = cls.get_request_info(id)
        rsp = request_info['rsp']

        if body:
            rsp.set_body(body)
        if headers:
            for name, val in headers.items():
                rsp.set_header(name, val)
        rsp.set_status(status)

        request_info['event'].set()
