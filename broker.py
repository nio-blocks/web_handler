from collections import defaultdict
from nio.modules.threading import Event, Lock


class RequestResponseBroker(object):

    _mappings = {}
    _locks = defaultdict(Lock)

    @classmethod
    def register_request(cls, id, req, rsp, timeout):
        """ Register that a request has occurred and wait for a response.

        Note, this method will block the current thread until the response
        is written or the timeout has occurred.

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

        # Let's release the lock for this request now that we've saved the
        # object in mappings.
        # We're going to first do a non-blocking acquire before releasing, in
        # case the lock is not locked
        req_lock = cls.get_lock(id)
        req_lock.acquire(False)
        req_lock.release()

        ev_result = req_event.wait(timeout)

        if not ev_result:
            # We timed out, write an error to the response
            cls.write_timeout_error(rsp)

        del cls._mappings[id]
        del cls._locks[id]

    @classmethod
    def get_lock(cls, id):
        return cls._locks[id]

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
        # Wait for the ability to acquire the lock before checking for the
        # request information
        with cls.get_lock(id):
            if id not in cls._mappings:
                raise ValueError("The request ID {} has not been "
                                "registered or has timed out".format(id))

        request_info = cls._mappings[id]
        rsp = request_info['rsp']

        if body:
            rsp.set_body(body)
        if headers:
            for name, val in headers.items():
                rsp.set_header(name, val)
        rsp.set_status(status)

        request_info['event'].set()
