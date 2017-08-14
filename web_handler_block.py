from .handler import Handler, JSONHandler

from nio.block.base import Block
from nio.modules.web import WebEngine
from nio.properties import StringProperty, IntProperty, \
    VersionProperty, TimeDeltaProperty


class WebHandler(Block):

    host = StringProperty(title='Host', default='0.0.0.0', visible=False)
    port = IntProperty(title='Port', default=8182)
    endpoint = StringProperty(title='Endpoint', default='')
    request_timeout = TimeDeltaProperty(
        title='Max Request Timeout', default={'days': 0, 'seconds': 10,
                                              'microseconds': 0})
    version = VersionProperty('1.0.0')

    def configure(self, context):
        super().configure(context)
        self._server = WebEngine.add_server(self.port(), self.host(), {})
        self._server.add_handler(self.get_handler())

    def get_handler(self):
        return Handler(self.endpoint(), self)

    def __init__(self):
        super().__init__()
        self._server = None

    def start(self):
        super().start()
        self.logger.debug("Starting server")
        self._server.start(None)

    def stop(self):
        self._server.stop()
        super().stop()

    def get_timeout_seconds(self):
        """ The REST Handler will use this to determine how long to wait """
        return self.request_timeout().total_seconds()

    def supports_method(self, method):
        """ Returns True if the block should support the given HTTP method """
        return True


class WebJSONHandler(WebHandler):

    version = VersionProperty("1.0.0")

    def get_handler(self):
        return JSONHandler(self.endpoint(), self)
