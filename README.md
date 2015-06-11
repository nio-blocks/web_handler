Web Handlers
===========

A suite of blocks that lets you build HTTP APIs using n.io services. In general, your service will have at least one of the following blocks, the `WebHandler` block and the `WebOutput` block. 

The `WebHandler` block will launch an HTTP server on the specified port and will notify signals when requests are made to that server. 

The `WebOutput` block is intended to respond to the requests made to the `WebHandler` block. These two blocks are "linked" by a request ID that will be notified on the signal by the `WebHandler` block and must be specified to the `WebOutput` block.

# WebHandler

## Properties
 * **Port** (int): The port to launch the server on. Be sure the port is not already in use
 * **Endpoint** (str): An optional endpoint to launch the server on. The URL that requests should be made to will follow the form `http://<HOST>:<PORT>/<ENDPOINT>
 * **Max Request Timeout** (timedelta): How long to give the service to respond to the request. If a corresponding WebOutput block does not write to the response for the incoming request in the specified time, a 504 Gateway Timed Out error will be returned to the caller. This is important to include in case an error in the service occurs.

## Dependencies
 * [WebServer Mixin](https://github.com/nio-blocks/mixins/tree/master/web_server)

## Commands
None

## Input
None

## Output
One signal per request, each with the following attributes

 * **id**: The unique request ID for this request. This value must carry along with the signal to the WebOutput block.
 * **method**: The HTTP method (i.e. `GET`, `POST`, etc) that the request was made with.
 * **params**: A dictionary containing any URL parameters passed to the request.
 * **headers**: A dictionary containing any request headers included in the request.
 * **body**: For some requests, the payload of the HTTP request
