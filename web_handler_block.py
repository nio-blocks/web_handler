from .mixins.web_server.web_server_block import WebServer
from .handler import Handler
from datetime import timedelta
from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.versioning.dependency import DependsOn
from nio.metadata.properties import StringProperty, IntProperty, \
    VersionProperty, TimeDeltaProperty


@DependsOn("nio.modules.web", "1.0.0")
@Discoverable(DiscoverableType.block)
class WebHandler(WebServer, Block):

    host = StringProperty(title='Host', default='0.0.0.0', visible=False)
    port = IntProperty(title='Port', default=8182)
    endpoint = StringProperty(title='Endpoint', default='')

    request_timeout = TimeDeltaProperty(
        title='Max Request Timeout', default=timedelta(seconds=10))

    version = VersionProperty('1.0.0')

    def configure(self, context):
        super().configure(context)
        self.configure_server({
            'host': self.host,
            'port': self.port
        }, Handler(self.endpoint, self))

    def start(self):
        super().start()
        # Start Web Server
        self._logger.debug("Starting server")
        self.start_server()

    def stop(self):
        # Stop Web Server
        self.stop_server()
        super().stop()

    def get_timeout_seconds(self):
        """ The REST Handler will use this to determine how long to wait """
        return self.request_timeout.total_seconds()

    def supports_method(self, method):
        """ Returns True if the block should support the given HTTP method """
        return True
