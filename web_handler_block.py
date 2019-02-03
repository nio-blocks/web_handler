from .handler import Handler, JSONHandler

from nio import GeneratorBlock
from nio.modules.web import WebEngine
from nio.properties import StringProperty, IntProperty, VersionProperty, \
                           ObjectProperty, TimeDeltaProperty, BoolProperty, \
                           PropertyHolder

class CORS(PropertyHolder):
    allow_origin = StringProperty(title='Access-Control-Allow-Origin',
                                  default='*',
                                  allow_none=True)
    allow_credentials = StringProperty(title='Access-Control-Allow-Credentials',
                                  default='true',
                                  allow_none=True)
    max_age = StringProperty(title='Access-Control-Max-Age',
                                  default=None,
                                  allow_none=True)
    expose_headers = StringProperty(title='Access-Control-Expose-Headers',
                                  default=None,
                                  allow_none=True)
    allow_methods = StringProperty(title='Access-Control-Allow-Methods',
                                  default='GET,POST,PUT,DELETE,OPTIONS',
                                  allow_none=True)
    allow_headers = StringProperty(title='Access-Control-Allow-Headers',
                                  default='Accept, Origin, Content-Type, Authorization',
                                  allow_none=True)

class WebHandler(GeneratorBlock):

    version = VersionProperty("1.1.0")
    host = StringProperty(title='Host', default='0.0.0.0', visible=False)
    port = IntProperty(title='Port', default=8182)
    endpoint = StringProperty(title='Endpoint', default='')
    auth = BoolProperty(title='Require Authentication', default=True)
    request_timeout = TimeDeltaProperty(title='Max Request Timeout',
                                        default={'days': 0,
                                                 'seconds': 10,
                                                 'microseconds': 0})
    ssl_enable = BoolProperty(title='Secure Sockets Layer (SSL) Enabled',
                              default=False)
    ssl_cert = StringProperty(title='SSL Certificate File',
                              default='',
                              allow_none=True)
    ssl_key = StringProperty(title='SSL Private Key File',
                             default='',
                             allow_none=True)

    cors = ObjectProperty(CORS,
                          title="Access-Control Headers",
                          default=dict(),
                          advanced=True)

    def configure(self, context):
        super().configure(context)
        config = {}
        if self.ssl_enable():
            self.logger.debug('Applying SSL certificate and private key')
            config = {
                'ssl_certificate': self.ssl_cert(),
                'ssl_private_key': self.ssl_key(),
            }
        if not self.auth():
            Handler.before_handler = self._no_auth

        self._server = WebEngine.add_server(self.port(), self.host(), config)
        self._server.add_handler(self.get_handler())

    def get_handler(self):
        return Handler(self.endpoint(), self.cors(), self)

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

    def _no_auth(self, request, response):
        """ Override before_handler so that authentication is not required """
        return

class WebJSONHandler(WebHandler):

    version = VersionProperty("1.1.0")

    def get_handler(self):
        return JSONHandler(self.endpoint(), self)
