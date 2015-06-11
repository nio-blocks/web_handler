import cherrypy
from nio.modules.threading import Event


class RequestResponseBroker(object):

    _mappings = {}

    @classmethod
    def register_request(cls, id, req, rsp, timeout):
        req_event = Event()
        cls._mappings[id] = {
            'req': req,
            'rsp': rsp,
            'timeout': timeout,
            'event': req_event
        }

        ev_result = req_event.wait(timeout)

        if not ev_result:
            # We timed out, write an error to the response
            cls.write_timeout_error(rsp)

        print("CHERRYPY STATUS IS {}".format(cherrypy.response.status))
        print(cherrypy.response)
        del cls._mappings[id]

    @classmethod
    def write_timeout_error(cls, rsp):
        rsp.set_status(504)
        rsp.set_body("The service did not respond in time")

    @classmethod
    def write_response(cls, id, status=200, body=None):
        if id not in cls._mappings:
            raise ValueError(
                "The request ID {} has not been registered".format(id))

        request_info = cls._mappings[id]
        rsp = request_info['rsp']

        if body:
            rsp.set_body(body)
        print("Setting status {}".format(status))
        rsp.set_status(status)

        request_info['event'].set()
